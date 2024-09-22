import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime

# Read the links from the text file
with open('document_links.txt', 'r') as file:
    links = file.readlines()

# Prepare lists to collect tweet data
datetimes = []
contents = []
retweets = []
favorites = []
presidents = []
categories_list = []
attributes_list = []
locations = []
document_links = []

# Function to safely convert date string to datetime object
def parse_datetime(datetime_str):
    try:
        return datetime.strptime(datetime_str, "%B %d, %Y%H:%M:%S")
    except ValueError:
        return None

# Loop through each link in the file
for link in links:
    link = link.strip()  # Remove any leading/trailing whitespace

    # Check if the link is a tweet link
    if 'tweets-' in link:
        print(f"Processing tweets from: {link}")
        
        # Send a request to the page
        response = requests.get(link)

        # Check if the request was successful
        if response.status_code == 200:
            # Parse the page content with Beautiful Soup
            soup = BeautifulSoup(response.text, 'html.parser')

            # Find the div containing tweet data
            tweet_section = soup.find('div', class_='field-docs-content')
            
            # Extract document-specific information (President, Categories, Attributes, Location) once per page
            president_tag = soup.find('div', class_='field-title')
            president_name = president_tag.get_text(strip=True) if president_tag else 'N/A'

            categories_section = soup.find('h3', text='Categories')
            categories = []
            if categories_section:
                categories_tags = categories_section.find_next_siblings('div')
                categories = [cat.get_text(strip=True) for cat in categories_tags]
            categories_combined = ', '.join(categories) if categories else 'N/A'

            attributes_section = soup.find('h3', text='Attributes')
            attributes = []
            if attributes_section:
                attributes_tags = attributes_section.find_next_siblings('div')
                attributes = [attr.get_text(strip=True) for attr in attributes_tags]
            attributes_combined = ', '.join(attributes) if attributes else 'N/A'

            location_tag = soup.find('div', class_='field-docs-location')
            location = location_tag.find('div', class_='field-spot-state').get_text(strip=True) if location_tag else 'N/A'
            
            # Find all tweet rows in the table and skip the first one
            if tweet_section:
                table = tweet_section.find('table')
                rows = table.find_all('tr')[1:]  # Skip the first row
                for row in rows:
                    cells = row.find_all('td')
                    if len(cells) == 2:
                        # Extract date and time as a single string
                        datetime_str = cells[0].get_text(strip=True).replace('\n', '')
                        
                        # Convert to datetime object
                        dt_object = parse_datetime(datetime_str)

                        # Extract tweet content, retweets, and favorites
                        content = cells[1].get_text(strip=True, separator=' ')
                        retweets_count = content.split('Retweets:')[1].split('Favorites:')[0].strip() if 'Retweets:' in content else '0'
                        favorites_count = content.split('Favorites:')[1].strip() if 'Favorites:' in content else '0'
                        tweet_text = content.split('Retweets:')[0].strip() if 'Retweets:' in content else content

                        # Append tweet-specific data to lists
                        datetimes.append(dt_object)
                        contents.append(tweet_text)
                        try:
                            retweets.append(int(retweets_count))
                        except ValueError:
                            retweets.append(0)
                        
                        try:
                            favorites.append(int(favorites_count))
                        except ValueError:
                            favorites.append(0)

                        # Append document-specific data for each tweet
                        presidents.append(president_name)
                        categories_list.append(categories_combined)
                        attributes_list.append(attributes_combined)
                        locations.append(location)
                        document_links.append(link)  # Append the link for each tweet
                        
            # if len(presidents) > 30:
            #     break
        else:
            print(f"Failed to retrieve page: {link}")

# Create a DataFrame from the collected tweet data
tweet_data = pd.DataFrame({
    'DateTime': datetimes,
    'Tweet': contents,
    'Retweets': retweets,
    'Favorites': favorites,
    'President': presidents,
    'Categories': categories_list,
    'Attributes': attributes_list,
    'Location': locations,
    'Link': document_links  # Include the link for each tweet
})

# Save the DataFrame to a CSV file
tweet_data.to_csv('tweets_data.csv', index=False)
print("Filtered and formatted tweets data has been saved to tweets_data.csv")