import discord
from discord.ext import commands
from discord import app_commands
from bot import is_authorized, is_blacklisted, blacklist, save_blacklist  # Import the helper functions and variables

class BlacklistCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="blacklist", description="Blacklist a user")
    @app_commands.describe(user="User to blacklist")
    async def blacklist(self, interaction: discord.Interaction, user: discord.User):
        if is_blacklisted(interaction.user.id):
            await interaction.response.send_message("You are blacklisted and cannot use any commands.", ephemeral=True)
            return
        if not is_authorized(interaction.user.id):
            await interaction.response.send_message("You are not authorized to use this command.", ephemeral=True)
            return
        blacklist.add(user.id)
        save_blacklist()
        await interaction.response.send_message(f'User {user.name} has been blacklisted.')

async def setup(bot):
    await bot.add_cog(BlacklistCommand(bot))
