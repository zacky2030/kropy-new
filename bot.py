import discord
from discord.ext import commands, tasks
import os
import json
import logging
from keep_alive import keep_alive  # Import the keep_alive function
import asyncio

# Initialize the bot with intents
intents = discord.Intents.default()
intents.members = True  # Required to work with member-related events
intents.presences = True
intents.message_content = True
bot = commands.Bot(command_prefix="k?", intents=intents)

 
 # User IDs allowed to use blacklist commands
AUTHORIZED_USERS = {'1190699873352290376', '882957554462892082', '865129062595035137'}

# Blacklist file paths
BLACKLIST_USER_FILE_PATH = './logs/blacklist_users.json'
BLACKLIST_SERVER_FILE_PATH = './logs/server_blacklist.json'

# Load blacklist from file
def load_blacklist(file_path):
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r') as f:
                return set(json.load(f))
        except json.JSONDecodeError:
            return set()
    else:
        return set()

user_blacklist = load_blacklist(BLACKLIST_USER_FILE_PATH)
server_blacklist = load_blacklist(BLACKLIST_SERVER_FILE_PATH)

# Save blacklist to file
def save_blacklist(blacklist, file_path):
    with open(file_path, 'w') as f:
        json.dump(list(blacklist), f)

# Check if the user is authorized
def is_authorized(user_id: int):
    return str(user_id) in AUTHORIZED_USERS

# Check if the user is blacklisted
def is_user_blacklisted(user_id: int):
    current_blacklist = load_blacklist(BLACKLIST_USER_FILE_PATH)
    return user_id in current_blacklist

# Check if the server is blacklisted
def is_server_blacklisted(server_id: int):
    current_blacklist = load_blacklist(BLACKLIST_SERVER_FILE_PATH)
    return server_id in current_blacklist







# Define the path to the config file
config_path = os.path.join(os.path.dirname(__file__), 'config.json')

# Read and parse the JSON file
with open(config_path, 'r') as config_file:
    config = json.load(config_file)

# Access the configuration values
token = config['token']  # Ensure the key matches the case in your JSON file
prefix = config['prefix']
owner_id = config['owner_id']

# Set the bot's status
@tasks.loop(minutes=5)  # Update status every 5 minutes
async def update_status():
    server_count = len(bot.guilds)
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.streaming, name=f"{server_count} servers | /statics",  url="https://twitch.tv/lunarjitsu"))

# Load slash commands from the commands folder
async def load_commands():
    for filename in os.listdir('./commands'):
        if filename.endswith('.py'):
            await bot.load_extension(f'commands.{filename[:-3]}')

# Load the cogs
async def load():
    await bot.load_extension('commands.automod_rule_create')
    await bot.load_extension('commands.automod_rule_delete')
    await bot.load_extension('commands.automod_rule_enable')
    await bot.load_extension('commands.automod_rule_disable')
    await bot.load_extension('cogs.join_leave_logs')
    await bot.load_extension('commands.ban')
    await bot.load_extension('commands.kick')
    await bot.load_extension('commands.timeout')

@bot.event
async def on_ready():
    await load_commands()
    await bot.tree.sync()
    update_status.start()  # Start the status update loop
    print(f'[READY] {bot.user.display_name} is Logged in as {bot.user}.')
    print(f"[STATUS] {bot.user.display_name}'s Status Succesfully set.")
    print(f"[TRIVIA] {bot.user.display_name}'s Trivia commands succesfully loaded.")
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} commands")
    except Exception as e:
        print(f"Failed to sync commands: {e}")

# Entry point for running the bot
async def main():
    keep_alive()  # Start the keep-alive server
    await bot.start(token)

# Ensure the code runs properly without using asyncio.run() directly
if __name__ == "__main__":
    asyncio.run(main())