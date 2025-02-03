import discord
from discord import app_commands
from dotenv import load_dotenv
import os
from aihandling import *
from concurrent.futures import ThreadPoolExecutor
load_dotenv()

discordkey = os.getenv('DISCORDKEY')

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

# Create thread pool for background tasks
thread_pool = ThreadPoolExecutor(max_workers=4)

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')
    try:
        synced = await tree.sync()
        print(f"Synced {len(synced)} command(s) globally")
        # Start request queue processor
        asyncio.create_task(process_request_queue())
    except Exception as e:
        print(e)

@tree.command(name="ask", description="Ask the AI assistant")
async def ask(interaction: discord.Interaction, prompt: str):
    await interaction.response.defer(thinking=True)
    try:
        res = await getresponse(prompt, interaction.user, str(interaction.guild_id))
        await interaction.followup.send(res)
    except Exception as e:
        await interaction.followup.send("Sorry, there was an error processing your request.")
        print(f"Error: {e}")

@tree.command(name="system", description="Set system message for AI (admin only)")
async def system(interaction: discord.Interaction, message: str):
    if interaction.user.guild_permissions.administrator:
        set_system_message(str(interaction.guild_id), message)
        await interaction.response.send_message("System message updated!", ephemeral=True)
    else:
        await interaction.response.send_message("You need admin permissions for this.", ephemeral=True)

@tree.command(name="timeout", description="Set conversation timeout in seconds (admin only)")
async def timeout(interaction: discord.Interaction, seconds: int):
    if interaction.user.guild_permissions.administrator:
        set_timeout(str(interaction.guild_id), seconds)
        await interaction.response.send_message(f"Timeout set to {seconds} seconds!", ephemeral=True)
    else:
        await interaction.response.send_message("You need admin permissions for this.", ephemeral=True)

@tree.command(name="status", description="Get conversation statistics")
async def status(interaction: discord.Interaction):
    user_id = f"{interaction.guild_id}-{interaction.user.id}"
    summary = get_conversation_summary(user_id)
    await interaction.response.send_message(summary, ephemeral=True)

@tree.command(name="help", description="Show available commands")
async def help(interaction: discord.Interaction):
    help_text = """
    **Available Commands**
    `/ask [prompt]` - Ask the AI something
    `/status` - View your conversation stats
    `/system [message]` - Set AI system message (admin)
    `/timeout [seconds]` - Set conversation timeout (admin)
    `/help` - Show this help message
    """
    await interaction.response.send_message(help_text, ephemeral=True)
 
client.run(discordkey)
