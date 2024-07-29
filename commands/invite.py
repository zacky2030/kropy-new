import discord
from discord import app_commands
from discord.ext import commands

class InviteCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="invite", description="Gives My Invite Link")
    async def invite(self, interaction: discord.Interaction):
        from bot import is_user_blacklisted, is_server_blacklisted  # Import the helper functions
        if is_user_blacklisted(interaction.user.id):
            await interaction.response.send_message("You r blacklisted and cannot use any commands.", ephemeral=True)
            return       
        if is_server_blacklisted(interaction.user.id):
            await interaction.response.send_message('This server is blacklisted and you cannot use any commands', ephemeral=True)
            return
        embed = discord.Embed(
            color=discord.Color.blue(),
            description="🥳 [Click For Invite](https://discord.com/api/oauth2/authorize?client_id=1261372969750368307&permissions=8&scope=bot%20applications.commands) | [Click For My Support Server](https://discord.gg/EkBnfKDFHQ)"
        )
        embed.set_author(
            name=interaction.user.name + "#" + interaction.user.discriminator,
            icon_url=interaction.user.display_avatar.url
        )
        embed.set_footer(
            text=f"{interaction.user.name}#{interaction.user.discriminator} Named User Used.",
            icon_url=interaction.user.display_avatar.url
        )
        embed.timestamp = discord.utils.utcnow()
        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(InviteCommand(bot))
