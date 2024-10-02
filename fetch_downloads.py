# fetch_downloads.py
import asyncio
import traceback
from scrape_spigot import fetch_spigot_download_count
from scrape_bukkit import fetch_bukkit_download_count

async def get_total_downloads():
    try:
        # Run download count fetch in an executor (to avoid blocking)
        loop = asyncio.get_event_loop()
        spigot_downloads = await loop.run_in_executor(None, fetch_spigot_download_count, "https://www.spigotmc.org/resources/nccasino.119847/")
        bukkit_downloads = await loop.run_in_executor(None, fetch_bukkit_download_count, "https://dev.bukkit.org/projects/nccasino")

        # Handle the case where Spigot fetching fails
        if spigot_downloads is None:
            print("Continuing with just Bukkit count for now.")
            spigot_downloads = 0

        # Calculate the total downloads if both fetches were successful
        if bukkit_downloads is not None:
            total_downloads = spigot_downloads + bukkit_downloads
            return total_downloads
        else:
            print("Failed to fetch Bukkit downloads.")
            return None
    except Exception as e:
        print(f"Error in get_total_downloads: {e}")
        traceback.print_exc()
        return None
