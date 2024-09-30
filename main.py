import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv
import os
from scrape_spigot import fetch_spigot_download_count
from scrape_bukkit import fetch_bukkit_download_count

# Load environment variables from .env file
load_dotenv()

# Get the token from the .env file
TOKEN = os.getenv('DISCORD_BOT_TOKEN')

# Discord bot intents
intents = discord.Intents.default()
intents.messages = True  # Enable message-related events

# Bot setup with prefix '!' 
bot = commands.Bot(command_prefix='!', intents=intents)

# Global variable to store the last download count.
last_total_downloads = 0

# Task to check the download counts every 5 minutes.
@tasks.loop(minutes=60)
async def check_downloads():
    global last_total_downloads
    
    # Fetch download counts from both Spigot and Bukkit.
    spigot_downloads = fetch_spigot_download_count("https://www.spigotmc.org/resources/nccasino.119847/")
    bukkit_downloads = fetch_bukkit_download_count("https://dev.bukkit.org/projects/nccasino")

    # Calculate total downloads
    if spigot_downloads is not None and bukkit_downloads is not None:
        total_downloads = spigot_downloads + bukkit_downloads
        
        # If the download count has changed, update the bot's activity
        if total_downloads != last_total_downloads:
            last_total_downloads = total_downloads
            # Update the bot's activity with the total downloads as a "watching" status
            await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f"Total Downloads: {total_downloads}"))
            print(f"Updated bot activity with total downloads: {total_downloads}")

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    # Start the background task to check downloads every 5 minutes
    check_downloads.start()

# Run the bot with the token
bot.run(TOKEN)
