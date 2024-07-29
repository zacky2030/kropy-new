import discord
from discord.ext import commands
from discord import app_commands
from bot import is_authorized, is_user_blacklisted, is_server_blacklisted, server_blacklist, save_blacklist, BLACKLIST_SERVER_FILE_PATH  # Import the helper functions and variables

class BlacklistServerCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="blacklist-server", description="Blacklist a server")
    @app_commands.describe(server_id="ID of the server to blacklist")
    async def blacklist_server(self, interaction: discord.Interaction, server_id: int):
        if is_user_blacklisted(interaction.user.id):
            await interaction.response.send_message("You are blacklisted and cannot use any commands.", ephemeral=True)
            return
        if is_server_blacklisted(interaction.user.id):
            await interaction.response.send_message('This server is blacklisted and you cannot use any commands', ephemeral=True)
            return
        if not is_authorized(interaction.user.id):
            await interaction.response.send_message("You are not authorized to use this command.", ephemeral=True)
            return
        server_blacklist.add(server_id)
        save_blacklist(server_blacklist, BLACKLIST_SERVER_FILE_PATH)
        await interaction.response.send_message(f'Server {server_id} has been blacklisted.')

    @app_commands.command(name="unblacklist-server", description="Remove a server from the blacklist")
    @app_commands.describe(server_id="ID of the server to unblacklist")
    async def unblacklist_server(self, interaction: discord.Interaction, server_id: int):
        if not is_authorized(interaction.user.id):
            await interaction.response.send_message("You are not authorized to use this command.", ephemeral=True)
            return
        if server_id in server_blacklist:
            server_blacklist.remove(server_id)
            save_blacklist(server_blacklist, BLACKLIST_SERVER_FILE_PATH)
            await interaction.response.send_message(f'Server {server_id} has been removed from the blacklist.')
        else:
            await interaction.response.send_message(f'Server {server_id} is not in the blacklist.')

async def setup(bot):
    await bot.add_cog(BlacklistServerCommand(bot))
