import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime

# Read links from the text file
with open('document_links.txt', 'r') as file:
    links = file.readlines()

# Prepare lists to store extracted data
titles = []
dates = []
contents = []
citations = []

# Function to safely convert date string to datetime object
def parse_date(date_str):
    try:
        # Attempt to parse the date; adjust formats as necessary
        return datetime.strptime(date_str, "%B %d, %Y")
    except ValueError as e:
        print(f"Date parsing error: {e} for date string: {date_str}")
        return None

# Loop through each link (modify range as needed for testing)
for link in links:
    link = link.strip()  # Clean up the link

    # Skip tweet links (already handled separately)
    if 'tweets-' not in link:
        print(f"Processing document from: {link}")

        try:
            # Send a request to the document page
            response = requests.get(link, timeout=10)
            response.raise_for_status()  # Raise an error for bad responses

            # Parse the page content with Beautiful Soup
            soup = BeautifulSoup(response.text, 'html.parser')

            # Find document title
            title_tag = soup.find('div', class_='field-ds-doc-title')
            title = title_tag.get_text(strip=True) if title_tag else 'N/A'

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

            # Append extracted data to lists
            titles.append(title)
            dates.append(date)
            contents.append(content_combined)
            citations.append(citation)

        except requests.exceptions.RequestException as req_err:
            print(f"Request error: {req_err} for link: {link}")
        except Exception as e:
            print(f"Unexpected error: {e} for link: {link}")

# Create a DataFrame to hold the extracted data
document_data = pd.DataFrame({
    'Title': titles,
    'Date': dates,
    'Content': contents,
    'Citation': citations
})

# Save the DataFrame to a CSV file
document_data.to_csv('documents_data.csv', index=False)
print("All document data has been saved to documents_data.csv")
