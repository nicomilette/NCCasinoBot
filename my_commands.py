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
        voice="echo",  # You can choose different voices like 'alloy', 'echo', 'fable', etc.
        input=text
    )
    response.stream_to_file(output_file)

# Add this global variable to keep track of the current voice client
active_voice_clients = {}

# Create a Button to stop the audio playback
class StopButton(discord.ui.View):
    def __init__(self, interaction: discord.Interaction):
        super().__init__(timeout=None)  # No timeout, the button stays active
        self.interaction = interaction

    @discord.ui.button(label="Stop Playback", style=discord.ButtonStyle.red)
    async def stop_button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            # Check if the bot is currently connected to a voice channel in this guild
            if interaction.guild.id in active_voice_clients:
                vc = active_voice_clients[interaction.guild.id]

                if vc.is_connected():
                    vc.stop()  # Stop the current audio playback
                    await vc.disconnect()  # Disconnect from the voice channel
                    
                    # Remove the guild from the active voice clients
                    del active_voice_clients[interaction.guild.id]

                    # Try to delete the original response (the stop button)
                    try:
                        await interaction.delete_original_response()
                    except discord.errors.NotFound:
                        # If the interaction token has expired, do nothing
                        pass
                else:
                    await interaction.response.send_message("The bot is not connected to any voice channel.", ephemeral=True)
            else:
                await interaction.response.send_message("No active audio playback to stop.", ephemeral=True)
        except Exception as e:
            try:
                await interaction.response.send_message(f"An error occurred: {e}", ephemeral=True)
            except discord.errors.NotFound:
                pass  # If the interaction has expired, silently fail

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
                # Join the voice channel and send the Stop button before playing audio
                channel = interaction.user.voice.channel
                vc = await channel.connect()

                # Save the voice client to the global dictionary to allow stopping later
                active_voice_clients[interaction.guild.id] = vc

                # Send the Stop button to the user before starting playback
                stop_view = StopButton(interaction)
                await interaction.followup.send(view=stop_view)  # Zero-width space with button

                # Convert the response text to speech, chunk by chunk, and play the audio
                for idx, chunk in enumerate(openai_chunks):
                    speech_file_path = Path(__file__).parent / f"response_{idx}.mp3"
                    await convert_text_to_speech(chunk, speech_file_path)
                    await play_audio(vc, str(speech_file_path))

                # After the audio has finished playing, delete the stop button message and send the plain text
                await interaction.delete_original_response()
                await interaction.channel.send(content=response_text)

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
                # Join the voice channel and send the Stop button before playing audio
                channel = interaction.user.voice.channel
                vc = await channel.connect()

                # Save the voice client to the global dictionary to allow stopping later
                active_voice_clients[interaction.guild.id] = vc

                # Send the Stop button to the user before starting playback
                stop_view = StopButton(interaction)
                await interaction.followup.send(view=stop_view)  # Zero-width space with button

                # Convert the input text to speech
                speech_file_path = Path(__file__).parent / "say_response.mp3"
                await convert_text_to_speech(input, speech_file_path)
                await play_audio(vc, str(speech_file_path))

                # After the audio has finished playing, delete the stop button message and send the plain text
                await interaction.delete_original_response()
                await interaction.channel.send(content=input)  # Sends the plain text without being a reply

            else:
                await interaction.followup.send("You are not in a voice channel!")

        except Exception as e:
            # Handle exceptions
            await interaction.followup.send(f"An error occurred: {e}")

    @bot.tree.command(name="stop", description="Stop the audio playback and disconnect the bot from the voice channel")
    async def stop(interaction: discord.Interaction):
        try:
            # Check if the bot is currently connected to a voice channel in this guild
            if interaction.guild.id in active_voice_clients:
                vc = active_voice_clients[interaction.guild.id]

                if vc.is_connected():
                    vc.stop()  # Stop the current audio playback
                    await vc.disconnect()  # Disconnect from the voice channel
                    
                    # Remove the guild from the active voice clients
                    del active_voice_clients[interaction.guild.id]
                    
                    # Send a message indicating the stop action was successful
                    if not interaction.response.is_done():
                        await interaction.response.send_message("Stopped the audio playback and disconnected from the voice channel.")
                    else:
                        await interaction.followup.send("Stopped the audio playback and disconnected from the voice channel.")
                else:
                    if not interaction.response.is_done():
                        await interaction.response.send_message("The bot is not connected to any voice channel.")
                    else:
                        await interaction.followup.send("The bot is not connected to any voice channel.")
            else:
                if not interaction.response.is_done():
                    await interaction.response.send_message("No active audio playback to stop.")
                else:
                    await interaction.followup.send("No active audio playback to stop.")
        except RuntimeError as e:
            # Handle case when session is already closed
            if str(e) == "Session is closed":
                print("Attempted to send a message after session was closed.")
            else:
                raise
        except Exception as e:
            # Catch any other exceptions and log them
            await interaction.followup.send(f"An unexpected error occurred: {e}")
