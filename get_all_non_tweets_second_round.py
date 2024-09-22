import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime

# Read the links from the text file
with open('document_links.txt', 'r') as file:
    all_links = [link.strip() for link in file.readlines()]

# Read the already processed links from the existing CSV (if it exists)
try:
    processed_data = pd.read_csv('documents_data.csv')
    processed_links = processed_data['Link'].tolist()
except FileNotFoundError:
    processed_links = []  # No CSV exists, so no links have been processed yet

# Identify uncollected links by comparing the two lists
uncollected_links = [link for link in all_links if link not in processed_links and 'tweets-' not in link]

# Prepare lists to store extracted data
titles = []
dates = []
contents = []
citations = []
presidents = []
categories_list = []
attributes_list = []
locations = []
document_links = []

# Function to safely convert date string to datetime object
def parse_date(date_str):
    try:
        # Attempt to parse the date; adjust formats as necessary
        return datetime.strptime(date_str, "%B %d, %Y")
    except ValueError as e:
        print(f"Date parsing error: {e} for date string: {date_str}")
        return None
    
    
print(f"Total uncollected links: {len(uncollected_links)}")

for link in uncollected_links:
    print(f"Processing document from: {link}")

    try:
        # Send a request to the document page
        response = requests.get(link, timeout=10)
        response.raise_for_status()  # Raise an error for bad responses

        # Parse the page content with Beautiful Soup
        soup = BeautifulSoup(response.text, 'html.parser')

        # Try to find the document title in multiple possible structures
        title = 'N/A'
        title_tag = soup.find('div', class_='field-ds-doc-title')
        if title_tag:
            # First try to find an <h1> inside the title div
            title = title_tag.find('h1').get_text(strip=True) if title_tag.find('h1') else 'N/A'
        elif soup.title:
            # Fallback to the <title> tag in the <head> if no specific title is found
            title = soup.title.get_text(strip=True)

        # Find document date
        date_tag = soup.find('div', class_='field-docs-start-date-time')
        date_str = date_tag.get_text(strip=True) if date_tag else 'N/A'
        date = parse_date(date_str) if date_str != 'N/A' else None

        # Find document content
        content_sections = soup.find_all('div', class_='field-docs-content')
        content_text = []
        for section in content_sections:
            paragraphs = section.find_all(['p', 'table'])
            for para in paragraphs:
                # Get text from paragraphs and any table data
                content_text.append(para.get_text(strip=True, separator=' '))

        content_combined = "\n".join(content_text) if content_text else 'N/A'

        # Find document citation
        citation_tag = soup.find('div', class_='field-prez-document-citation')
        citation = citation_tag.get_text(strip=True) if citation_tag else 'N/A'

        # Try to find the president name in multiple possible structures
        president_name = 'N/A'
        president_tag = soup.find('div', class_='field-title')
        if president_tag:
            president_name = president_tag.find('a').get_text(strip=True) if president_tag.find('a') else 'N/A'

        # Find categories
        categories_section = soup.find('h3', string='Categories')
        categories = []
        if categories_section:
            categories_tags = categories_section.find_next_siblings('div')
            categories = [cat.get_text(strip=True) for cat in categories_tags]
        categories_combined = ', '.join(categories) if categories else 'N/A'

        # Find attributes
        attributes_section = soup.find('h3', string='Attributes')
        attributes = []
        if attributes_section:
            attributes_tags = attributes_section.find_next_siblings('div')
            attributes = [attr.get_text(strip=True) for attr in attributes_tags]
        attributes_combined = ', '.join(attributes) if attributes else 'N/A'

        # Find location
        location_tag = soup.find('div', class_='field-docs-location')
        location = location_tag.find('div', class_='field-spot-state').get_text(strip=True) if location_tag else 'N/A'

        # Append extracted data to lists
        titles.append(title)
        dates.append(date)
        contents.append(content_combined)
        citations.append(citation)
        presidents.append(president_name)
        categories_list.append(categories_combined)
        attributes_list.append(attributes_combined)
        locations.append(location)
        document_links.append(link)  # Store the link as well

    except requests.exceptions.RequestException as req_err:
        print(f"Request error: {req_err} for link: {link}")
    except Exception as e:
        print(f"Unexpected error: {e} for link: {link}")

# Create a DataFrame to hold the new extracted data
new_document_data = pd.DataFrame({
    'Title': titles,
    'Date': dates,
    'Content': contents,
    'Citation': citations,
    'President': presidents,
    'Categories': categories_list,
    'Attributes': attributes_list,
    'Location': locations,
    'Link': document_links  # Add the link column
})

# If there is existing data, append the new data to it
if not new_document_data.empty:
    if processed_links:
        document_data = pd.concat([processed_data, new_document_data], ignore_index=True)
    else:
        document_data = new_document_data

    # Save the combined DataFrame to a CSV file
    document_data.to_csv('documents_data.csv', index=False)
    print(f"All new document data has been appended and saved to documents_data.csv")
else:
    print("No new data was collected.")