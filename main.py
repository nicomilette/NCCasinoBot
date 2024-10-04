import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv
import os
import traceback
import asyncio
from fetch_downloads import get_total_downloads  # Existing logic for fetching downloads
from my_commands import register_commands  # Slash command logic

# Load environment variables from .env file
load_dotenv()

# Get the bot tokens from the .env file
NICOBOT_TOKEN = os.getenv('NICOBOT_TOKEN')
NCCASINO_TOKEN = os.getenv('NCCASINO_TOKEN')

# Set up intents for NICOBOT and NCCASINO
nicobot_intents = discord.Intents.default()
nicobot_intents.messages = True
nicobot_intents.presences = True

nccasino_intents = discord.Intents.default()
nccasino_intents.voice_states = True  # Enable voice event handling
nccasino_intents.messages = True

# Create bot instances
nicobot = commands.Bot(command_prefix='!', intents=nicobot_intents)
nccasino_bot = commands.Bot(command_prefix='?', intents=nccasino_intents)

# Global variable to store the last download count for NCCASINO bot
last_total_downloads = 0

# Task to check the download counts every 60 minutes (NCCASINO bot)
@tasks.loop(minutes=60)
async def check_downloads():
    global last_total_downloads
    try:
        total_downloads = await get_total_downloads()
        if total_downloads != last_total_downloads:
            last_total_downloads = total_downloads
            await nccasino_bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f"Total Downloads: {total_downloads}"))
            print(f"Updated NCCASINO bot activity with total downloads: {total_downloads}")
    except Exception as e:
        print(f"Error in check_downloads: {e}")
        traceback.print_exc()

# Event to sync slash commands globally for NICOBOT
@nicobot.event
async def on_ready():
    print(f'NICOBOT logged in as {nicobot.user}')
    
    # Sync slash commands globally for NICOBOT
    await nicobot.tree.sync()
    print("NICOBOT slash commands synced globally.")

# Event to sync slash commands globally for NCCASINO
@nccasino_bot.event
async def on_ready():
    print(f'NCCASINO logged in as {nccasino_bot.user}')
    
    # Sync slash commands globally for NCCASINO
    await nccasino_bot.tree.sync()
    print("NCCASINO slash commands synced globally.")

    # Start the download checking loop
    check_downloads.start()

# Register slash commands for NICOBOT
register_commands(nicobot)

# Error handling for any uncaught errors in NICOBOT
@nicobot.event
async def on_error(event, *args, **kwargs):
    print(f"NICOBOT error occurred: {traceback.format_exc()}")

# Error handling for any uncaught errors in NCCASINO
@nccasino_bot.event
async def on_error(event, *args, **kwargs):
    print(f"NCCASINO error occurred: {traceback.format_exc()}")

# Main function to run both bots
async def main():
    # Start both bots asynchronously
    await asyncio.gather(
        nicobot.start(NICOBOT_TOKEN),
        nccasino_bot.start(NCCASINO_TOKEN)
    )

# Run the main function
if __name__ == '__main__':
    asyncio.run(main())
