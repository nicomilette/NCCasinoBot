from zenrows import ZenRowsClient
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

def fetch_spigot_download_count(url):
    # Get the API key from the environment
    api_key = os.getenv("ZENROWS_API_KEY")
    
    if not api_key:
        print("ZenRows API key not found. Please set it in the .env file.")
        return None

    # Initialize the ZenRows client with the API key
    client = ZenRowsClient(api_key)
    params = {"js_render": "true"}
    
    # Fetch the page
    response = client.get(url, params=params)
    
    if response.status_code == 200:
        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find the download count (based on your HTML structure)
        download_count_tag = soup.find('dl', class_='downloadCount')
        if download_count_tag:
            download_count = download_count_tag.find('dd').text.strip()
            return int(download_count.replace(",", ""))  # Convert to integer, removing commas
        else:
            print("Download count not found on Spigot.")
            return None
    else:
        print(f"Failed to retrieve Spigot page. Status code: {response.status_code}")
        return None
