import discord
from discord.ext import commands
from discord import app_commands
import asyncio

class DmUser(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="dm", description="DM a user")
    @app_commands.describe(user="Select the user to DM me!", message="The message to send me")
    @app_commands.default_permissions(manage_messages=True)
    async def dm(self, interaction: discord.Interaction, user: discord.Member, message: str):
        from bot import is_user_blacklisted, is_server_blacklisted  # Import the helper functions
        if is_user_blacklisted(interaction.user.id):
            await interaction.response.send_message("You r blacklisted and cannot use any commands.", ephemeral=True)
            return       
        if is_server_blacklisted(interaction.user.id):
            await interaction.response.send_message('This server is blacklisted and you cannot use any commands', ephemeral=True)
            return
        memberid = interaction.user.id

        if user.id == self.bot.user.id:
            await interaction.response.send_message("**I cannot send _DM_ to myself!**", ephemeral=True)
            return

        try:
            await user.send(message)
            await interaction.response.send_message(f"Successfully sent DM message to <@{user.id}>", ephemeral=True)
        except Exception as err:
            print(err)
            await interaction.response.send_message(f"Failed to send DM message to **<@{user.id}>**", ephemeral=True)

        await asyncio.sleep(3.5)
        await interaction.delete_original_response()

async def setup(bot):
    await bot.add_cog(DmUser(bot))
