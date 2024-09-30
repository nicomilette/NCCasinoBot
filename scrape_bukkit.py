import requests
from bs4 import BeautifulSoup

def fetch_bukkit_download_count(url):
    response = requests.get(url)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find all info-labels and corresponding info-data
        labels = soup.find_all('div', class_='info-label')
        values = soup.find_all('div', class_='info-data')
        
        # Loop through labels to find "Total Downloads" and get the corresponding value
        for label, value in zip(labels, values):
            if 'Total Downloads' in label.text:
                download_count = value.text.strip()
                return int(download_count.replace(",", ""))  # Convert to integer, removing commas
        
        print("Total Downloads not found on Bukkit.")
        return None
    else:
        print(f"Failed to retrieve Bukkit page. Status code: {response.status_code}")
        return None
