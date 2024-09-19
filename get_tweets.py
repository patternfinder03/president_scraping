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
            
            # Find all tweet rows in the table
            if tweet_section:
                table = tweet_section.find('table')
                rows = table.find_all('tr')
                for row in rows:
                    cells = row.find_all('td')
                    if len(cells) == 2:
                        # Extract date and time as a single string
                        datetime_str = cells[0].get_text(strip=True).replace('\n', '')
                        
                        try:
                            # Convert the string into a datetime object
                            dt_object = datetime.strptime(datetime_str, "%B %d, %Y%H:%M:%S")
                        except ValueError:
                            # Skip rows that do not match the expected format
                            continue
                        
                        # Extract tweet content, retweets, and favorites
                        content = cells[1].get_text(strip=True, separator=' ')
                        retweets_count = content.split('Retweets:')[1].split('Favorites:')[0].strip() if 'Retweets:' in content else '0'
                        favorites_count = content.split('Favorites:')[1].strip() if 'Favorites:' in content else '0'
                        tweet_text = content.split('Retweets:')[0].strip() if 'Retweets:' in content else content
                        
                        # Append to lists
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
        else:
            print(f"Failed to retrieve page: {link}")

# Create a DataFrame from the collected tweet data
tweet_data = pd.DataFrame({
    'DateTime': datetimes,
    'Tweet': contents,
    'Retweets': retweets,
    'Favorites': favorites
})

# Save the DataFrame to a CSV file
tweet_data.to_csv('tweets_data.csv', index=False)
print("Filtered and formatted tweets data has been saved to tweets_data.csv")
