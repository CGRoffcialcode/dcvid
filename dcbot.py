import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import traceback 
TOKEN = "MTMxMjE1NDg3MTEwNDkzMzkyOQ.GCx9Wl.JeuuXE5Mrgp-lN9Efllp1sL5KnzYpcFZkumrbA"


if TOKEN is None:
    print("Error: DISCORD_TOKEN not found in .env file.")
    exit(1)

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='/', intents=intents)

@bot.tree.command(name="find_video", description="Finds a video by its unique ID.")
async def find_video(interaction: discord.Interaction, unique_id: str):
    print(type(interaction))
    await interaction.response.defer(ephemeral=True)  # Crucial deferral

    channel_id = 1309979095576084632  # Replace with your channel ID. Consider loading from config

    try:
        channel = bot.get_channel(channel_id)
        if not channel:
            await interaction.followup.send("Channel not found.", ephemeral=True)
            return

        async for message in channel.history(limit=None):
            if f"Unique ID: {unique_id}" in message.content:
                await interaction.followup.send(f"Found video: {message.jump_url}", ephemeral=True)
                return

        await interaction.followup.send(f"Video with ID '{unique_id}' not found.", ephemeral=True)

    except discord.Forbidden:
        await interaction.followup.send("Bot lacks permission to read message history.", ephemeral=True)
    except discord.HTTPException as e:
        await interaction.followup.send(f"An error occurred: {e}", ephemeral=True)
    except Exception as e:
        print(f"Error searching channel history: {e}")
        traceback.print_exc()
        print(type(interaction))


@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    print("Syncing commands...")
    await bot.tree.sync()
    print("Commands synced.")


bot.run(TOKEN)