from zenrows import ZenRowsClient
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

def fetch_spigot_download_count(url):
    # Get the ZenRows API key from the environment
    api_key = os.getenv("ZENROWS_API_KEY")
    
    if not api_key:
        print("ZenRows API key not found. Please set it in the .env file.")
        return None

    # Initialize ZenRows client with the API key
    client = ZenRowsClient(api_key)
    params = {"js_render": "true"}

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
                print("Download count not found on Spigot page.")
                return None
        else:
            print(f"Failed to retrieve Spigot page. Status code: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error occurred: {e}")
        return None
