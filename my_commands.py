# my_commands.py
import discord
from discord import app_commands
from openai import OpenAI
from dotenv import load_dotenv
import os
from pathlib import Path
import asyncio

# Load environment variables from .env file
load_dotenv()

# Get the OpenAI API key
api_key = os.getenv("OPENAI_API_KEY")

# Initialize the OpenAI client
client_openai = OpenAI(api_key=api_key)

# Helper function to split long messages into chunks for Discord's 2000-char limit
def split_into_chunks(text, max_length=2000):
    return [text[i:i + max_length] for i in range(0, len(text), max_length)]

# Helper function to split input text into chunks for OpenAI (4096 character limit)
def split_for_openai(text, max_length=4096):
    return [text[i:i + max_length] for i in range(0, len(text), max_length)]

# Helper function to play audio in a voice channel
async def play_audio(vc, audio_source):
    vc.play(discord.FFmpegPCMAudio(audio_source), after=lambda e: print('done', e))
    while vc.is_playing():
        await asyncio.sleep(1)
    await vc.disconnect()

# Helper function to convert text to speech using OpenAI
async def convert_text_to_speech(text, output_file):
    client = OpenAI(api_key=api_key)
    response = client.audio.speech.create(
        model="tts-1",
        voice="alloy",  # You can choose different voices like 'alloy', 'echo', 'fable', etc.
        input=text
    )
    response.stream_to_file(output_file)

# Register slash commands
def register_commands(bot):

    # New slash command to query OpenAI
    @bot.tree.command(name="query", description="Ask a question to OpenAI and stream the response as audio")
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

            response_text = completion.choices[0].message.content

            # Split the response for OpenAI TTS input (4096 char limit)
            openai_chunks = split_for_openai(response_text, max_length=4096)

            # Check if the user is in a voice channel
            if interaction.user.voice:
                # Convert the response text to speech, chunk by chunk
                for idx, chunk in enumerate(openai_chunks):
                    speech_file_path = Path(__file__).parent / f"response_{idx}.mp3"
                    await convert_text_to_speech(chunk, speech_file_path)

                    # Join the voice channel and play the audio
                    channel = interaction.user.voice.channel
                    vc = await channel.connect()
                    await play_audio(vc, str(speech_file_path))

                # After the audio has finished playing, send the text response in chunks
                for chunk in split_into_chunks(response_text):
                    await interaction.followup.send(chunk)

            # If the user is not in a voice channel, send the text response in chunks immediately
            else:
                for chunk in split_into_chunks(response_text):
                    await interaction.followup.send(chunk)

        except Exception as e:
            # Handle exceptions
            await interaction.followup.send(f"An error occurred: {e}")

    # New slash command to take input text and play it as TTS in the voice channel
    @bot.tree.command(name="say", description="Convert input text to speech and play in the voice channel")
    async def say(interaction: discord.Interaction, input: str):
        # Defer the response to prevent interaction timeout
        await interaction.response.defer()

        try:
            # Check if the user is in a voice channel
            if interaction.user.voice:
                # Convert the input text to speech
                speech_file_path = Path(__file__).parent / "say_response.mp3"
                await convert_text_to_speech(input, speech_file_path)

                # Join the voice channel and play the audio
                channel = interaction.user.voice.channel
                vc = await channel.connect()
                await play_audio(vc, str(speech_file_path))

                # Send confirmation after the audio is played
                await interaction.followup.send(f"{input}")

            else:
                await interaction.followup.send("You are not in a voice channel!")

        except Exception as e:
            # Handle exceptions
            await interaction.followup.send(f"An error occurred: {e}")
