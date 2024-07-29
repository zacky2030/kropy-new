import discord
from discord import app_commands
from discord.ext import commands

class AvatarCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="avatar", description="Show the user's avatar.")
    @app_commands.describe(user="Target user to get the avatar.")
    async def avatar(self, interaction: discord.Interaction, user: discord.User = None):
        from bot import is_user_blacklisted, is_server_blacklisted  # Import the helper functions
        if is_user_blacklisted(interaction.user.id):
            await interaction.response.send_message("You r blacklisted and cannot use any commands.", ephemeral=True)
            return       
        if is_server_blacklisted(interaction.user.id):
            await interaction.response.send_message('This server is blacklisted and you cannot use any commands', ephemeral=True)
            return
        user = user or interaction.user
        embed = discord.Embed(
            color=discord.Color.blue()
        )
        embed.set_author(
            name=f"{self.bot.user.name} Avatar System",
            icon_url=interaction.user.display_avatar.url
        )
        embed.set_image(url=user.display_avatar.url)
        embed.set_footer(
            text=f"{interaction.user.name}#{interaction.user.discriminator} Named Member Used.",
            icon_url=interaction.user.display_avatar.url
        )
        embed.timestamp = discord.utils.utcnow()
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(AvatarCommand(bot))
