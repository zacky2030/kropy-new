import discord
from discord.ext import commands
from discord import app_commands
from bot import is_authorized, is_blacklisted, blacklist, save_blacklist  # Import the helper functions and variables

class DeblacklistCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="deblacklist", description="Remove a user from the blacklist")
    @app_commands.describe(user="User to de-blacklist")
    async def deblacklist(self, interaction: discord.Interaction, user: discord.User):
        if is_blacklisted(interaction.user.id) and user.id != interaction.user.id:
            await interaction.response.send_message("You are blacklisted and cannot use any commands.", ephemeral=True)
            return
        if not is_authorized(interaction.user.id) and user.id != interaction.user.id:
            await interaction.response.send_message("You are not authorized to use this command.", ephemeral=True)
            return
        if user.id in blacklist:
            blacklist.remove(user.id)
            save_blacklist()
            await interaction.response.send_message(f'User {user.name} has been removed from the blacklist.')
        else:
            await interaction.response.send_message(f'User {user.name} is not in the blacklist.')

async def setup(bot):
    await bot.add_cog(DeblacklistCommand(bot))
