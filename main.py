# main.py
import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv
import os
import traceback
from fetch_downloads import get_total_downloads  # Existing logic for fetching downloads
from my_commands import register_commands  # Slash command logic

# Load environment variables from .env file
load_dotenv()

# Get the bot token from the .env file
TOKEN = os.getenv('DISCORD_BOT_TOKEN')

# Set up intents for voice states and messages
intents = discord.Intents.default()
intents.messages = True
intents.presences = True
intents.voice_states = True  # Enable voice event handling

# Create bot instance
bot = commands.Bot(command_prefix='!', intents=intents)

# Global variable to store the last download count
last_total_downloads = 0

# Task to check the download counts every 60 minutes
@tasks.loop(minutes=60)
async def check_downloads():
    global last_total_downloads
    try:
        total_downloads = await get_total_downloads()
        if total_downloads != last_total_downloads:
            last_total_downloads = total_downloads
            await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f"Total Downloads: {total_downloads}"))
            print(f"Updated bot activity with total downloads: {total_downloads}")
    except Exception as e:
        print(f"Error in check_downloads: {e}")
        traceback.print_exc()

# Event to sync slash commands globally
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    
    # Sync slash commands globally
    await bot.tree.sync()
    print("Slash commands synced globally.")

    # Start the download checking loop
    check_downloads.start()

# Register slash commands in the command handler
register_commands(bot)

# Error handling for any uncaught errors
@bot.event
async def on_error(event, *args, **kwargs):
    print(f"An error occurred: {traceback.format_exc()}")

# Run the bot
bot.run(TOKEN)
