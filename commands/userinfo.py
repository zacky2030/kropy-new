import discord
from discord import app_commands
from discord.ext import commands

class UserInfoCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="userinfo", description="Displays information about a user")
    @app_commands.describe(user="The user to get information about")
    async def userinfo(self, interaction: discord.Interaction, user: discord.User = None):
        from bot import is_user_blacklisted, is_server_blacklisted  # Import the helper functions
        if is_user_blacklisted(interaction.user.id):
            await interaction.response.send_message("You r blacklisted and cannot use any commands.", ephemeral=True)
            return       
        if is_server_blacklisted(interaction.user.id):
            await interaction.response.send_message('This server is blacklisted and you cannot use any commands', ephemeral=True)
            return
        user = user or interaction.user
        member = interaction.guild.get_member(user.id)

        embed = discord.Embed(
            title=f"User Info - {user}",
            color=discord.Color.blue()
        )
        embed.set_thumbnail(url=user.display_avatar.url)
        embed.add_field(name="Username", value=user.name, inline=True)
        embed.add_field(name="Discriminator", value=f"#{user.discriminator}", inline=True)
        embed.add_field(name="ID", value=user.id, inline=True)
        embed.add_field(name="Bot", value=user.bot, inline=True)

        if member:
            embed.add_field(name="Nickname", value=member.nick, inline=True)
            embed.add_field(name="Joined Server", value=member.joined_at.strftime("%Y-%m-%d %H:%M:%S"), inline=True)
            embed.add_field(name="Top Role", value=member.top_role.mention, inline=True)

        embed.set_footer(
            text=f"Requested by {interaction.user}",
            icon_url=interaction.user.display_avatar.url
        )
        embed.timestamp = discord.utils.utcnow()

        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(UserInfoCommand(bot))
