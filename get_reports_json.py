import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
import json

def get_field_docs_content(url):
    try:
        # Send a GET request to the URL
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors
        
        # Parse the HTML content with BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all div elements with class 'field-docs-content'
        divs = soup.find_all('div', class_='field-docs-content')
        
        reports = []
        
        for div in divs:
            # Find all table rows within each div
            tables = div.find_all('table')
            # print("Found table: ", tables)
            for table in tables:
                # Extract headers and body rows
                rows = table.find_all('tr')
                
                for row in rows[1:]:  # Skip the header row
                    cells = row.find_all('td')
                    
                    if len(cells) == 2:
                        sent = cells[0].get_text(strip=True)[:-5] + " " + cells[0].get_text(strip=True)[-5:]
                        report = cells[1].get_text(strip=True)
                        reports.append((sent, report))
        
        return reports
        
    except requests.RequestException as e:
        print(f"Error fetching the URL: {e}")
        return []

def extract_pool_reports_links(html_content):
    # Parse the HTML content
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Find all <a> tags where the text contains "Pool Reports of"
    links = soup.find_all('a', string=lambda text: text and "Pool Reports of" in text)
    
    # Extract the href attributes
    hrefs = [link.get('href') for link in links]
    
    return hrefs

def get_pool_reports_from_link(url):
    try:
        # Send a GET request to the URL
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors
        links = extract_pool_reports_links(response.text)
        d = {}
        for link in tqdm(links):
            d[link] = get_field_docs_content("https://www.presidency.ucsb.edu/" + link)
        return d
    except requests.RequestException as e:
        print(f"Error fetching the URL: {e}")
        return []

# start_link = "https://www.presidency.ucsb.edu/documents/app-categories/pool-reports?items_per_page=1000&field_docs_start_date_time_value%5Bvalue%5D%5Bdate%5D="
# years = [2017, 2018, 2019, 2020]
overall = {}
years = [2020]
links = ["https://www.presidency.ucsb.edu/documents/app-categories/pool-reports?items_per_page=1000&field_docs_start_date_time_value%5Bvalue%5D%5Bdate%5D=2020"]

for link, year in tqdm(zip(links, years)):
    overall[year] = get_pool_reports_from_link(link)

# Example usage
url = 'https://www.presidency.ucsb.edu/documents/pool-reports-december-31-2020'
content = get_field_docs_content(url)
# print(content)

results_file = open("results.json", "w+")
results_file.write(json.dumps(overall))
results_file.close()