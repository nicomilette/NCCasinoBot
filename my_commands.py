# my_commands.py
import discord
from discord import app_commands
from openai import OpenAI
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Get the OpenAI API key
api_key = os.getenv("OPENAI_API_KEY")

# Initialize the OpenAI client
client_openai = OpenAI(api_key=api_key)

# Register slash commands
def register_commands(bot):

    # New slash command to query OpenAI
    @bot.tree.command(name="query", description="Ask a question to OpenAI")
    async def query(interaction: discord.Interaction, question: str):
        # Defer the response to prevent interaction timeout
        await interaction.response.defer()

        try:
            # Call OpenAI API with the user's input
            completion = client_openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": question}
                ]
            )

            # Correct way to access the response content
            response = completion.choices[0].message.content

            # Send the result back to the user
            await interaction.followup.send(response)

        except Exception as e:
            # Handle exceptions
            await interaction.followup.send(f"An error occurred: {e}")
