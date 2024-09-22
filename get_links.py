import requests
from bs4 import BeautifulSoup

def scrape_presidency_links(base_urls_with_max_pages):
    # List to store all document links
    all_links = []

    # Loop through each base URL and the number of pages to scrape
    for base_url, max_pages in base_urls_with_max_pages:
        for page in range(0, max_pages + 1):
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
                print(f"Failed to retrieve page {page} for {base_url}")

    # Print the total number of collected links
    print(f"Total links collected: {len(all_links)}")

    # Save all the links to a file
    with open("document_links.txt", "w") as file:
        for link in all_links:
            file.write(link + "\n")

    print(f"Total links collected: {len(all_links)}")
    print("All links have been saved to document_links.txt")

# List of base URLs with the corresponding max number of pages to scrape
# Format: [(base_url_1, max_pages_1), (base_url_2, max_pages_2), ...]
base_urls_with_max_pages = [
    ("https://www.presidency.ucsb.edu/advanced-search?field-keywords=&field-keywords2=&field-keywords3=&from%5Bdate%5D=&to%5Bdate%5D=&person2=200301&items_per_page=25&page=", 482),
    ("https://www.presidency.ucsb.edu/advanced-search?field-keywords=&field-keywords2=&field-keywords3=&from%5Bdate%5D=&to%5Bdate%5D=&person2=200320&items_per_page=25&page=", 627),
    ("https://www.presidency.ucsb.edu/advanced-search?field-keywords=&field-keywords2=&field-keywords3=&from%5Bdate%5D=&to%5Bdate%5D=&person2=200300&items_per_page=25&page=", 741),
    ("https://www.presidency.ucsb.edu/advanced-search?field-keywords=&field-keywords2=&field-keywords3=&from%5Bdate%5D=&to%5Bdate%5D=&person2=200297&items_per_page=25&page=", 291)
]

# Call the function to start scraping
scrape_presidency_links(base_urls_with_max_pages)
