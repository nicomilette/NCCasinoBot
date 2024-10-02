from zenrows import ZenRowsClient
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os
import time  # Import the time module to implement delays between retries

# Load environment variables from .env file
load_dotenv()

def fetch_spigot_download_count(url, retries=10, delay=2):

    # Get the ZenRows API key from the environment
    api_key = os.getenv("ZENROWS_API_KEY")
    
    if not api_key:
        print("ZenRows API key not found. Please set it in the .env file.")
        return None

    # Initialize ZenRows client with the API key
    client = ZenRowsClient(api_key)
    params = {"js_render": "true"}

    for attempt in range(retries):
        try:
            # Fetch the page using ZenRows
            response = client.get(url, params=params)
            
            if response.status_code == 200:
                # Parse the HTML content using BeautifulSoup
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Locate the total download count in the HTML structure
                download_count_tag = soup.find('dl', class_='downloadCount')
                if download_count_tag:
                    download_count = download_count_tag.find('dd').text.strip()
                    return int(download_count.replace(",", ""))  # Convert to integer, removing commas
                else:
                    print(f"Download count not found on Spigot page. Retry {attempt + 1}/{retries}")
            else:
                print(f"Failed to retrieve Spigot page. Status code: {response.status_code}. Retry {attempt + 1}/{retries}")
        except Exception as e:
            print(f"Error occurred: {e}. Retry {attempt + 1}/{retries}")

        # Wait before retrying
        time.sleep(delay)
    
    # After all retries, return None if the download count is not found
    print("Failed to retrieve the download count after retries.")
    return None
