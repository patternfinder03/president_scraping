import requests
from bs4 import BeautifulSoup

# Base URL for the pages
base_url = "https://www.presidency.ucsb.edu/advanced-search?field-keywords=&field-keywords2=&field-keywords3=&from%5Bdate%5D=&to%5Bdate%5D=&person2=200301&items_per_page=25&page="

# List to store all document links
all_links = []

# Loop through all pages from 1 to 482
for page in range(0, 483):
    # Construct the page URL
    url = f"{base_url}{page}"
    print(f"Scraping page: {page} - {url}")
    
    # Send a request to the page
    response = requests.get(url)
    
    # Check if the request was successful
    if response.status_code == 200:
        # Parse the page content with Beautiful Soup
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all document links within the table
        table = soup.find('table', class_='views-table')
        if table:
            links = table.find_all('a', href=True)
            for link in links:
                # Filter out non-document links
                if "/documents/" in link['href']:
                    full_link = "https://www.presidency.ucsb.edu" + link['href']
                    all_links.append(full_link)
                    print(full_link)
    else:
        print(f"Failed to retrieve page {page}")

# Print the total number of collected links
print(f"Total links collected: {len(all_links)}")


with open("document_links.txt", "w") as file:
    for link in all_links:
        file.write(link + "\n")

print(f"Total links collected: {len(all_links)}")
print("All links have been saved to document_links.txt")