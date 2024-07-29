import discord
from discord import app_commands
from discord.ext import commands

class LockCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="lock", description="Locks the channel, disabling @everyone from sending messages")
    async def lock(self, interaction: discord.Interaction):
        from bot import is_user_blacklisted, is_server_blacklisted  # Import the helper functions
        if is_user_blacklisted(interaction.user.id):
            await interaction.response.send_message("You r blacklisted and cannot use any commands.", ephemeral=True)
            return       
        if is_server_blacklisted(interaction.user.id):
            await interaction.response.send_message('This server is blacklisted and you cannot use any commands', ephemeral=True)
            return
        if not interaction.user.guild_permissions.manage_channels : 
            await interaction.response.send_message("You dont have the right permission to lock the channel", ephemeral=True)
            return
        if not interaction.guild.me.guild_permissions.manage_channels :
            await interaction.response.send_message("I dont have manage channels permissions to lock the channel", ephemeral=True)
            return
        

        channel = interaction.channel
        everyone_role = interaction.guild.default_role

        # Disable @everyone from sending messages
        await channel.set_permissions(everyone_role, send_messages=False)

        embed = discord.Embed(
            title="Channel Locked",
            description=f"The channel {channel.mention} has been locked. @everyone can no longer send messages.",
            color=discord.Color.red()
        )
        embed.set_footer(
            text=f"Locked by {interaction.user}",
            icon_url=interaction.user.display_avatar.url
        )
        embed.timestamp = discord.utils.utcnow()

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="unlock", description="Unlocks the channel, allowing @everyone to send messages")
    async def unlock(self, interaction: discord.Interaction):
        from bot import is_user_blacklisted, is_server_blacklisted  # Import the helper functions
        if is_user_blacklisted(interaction.user.id):
            await interaction.response.send_message("You r blacklisted and cannot use any commands.", ephemeral=True)
            return       
        if is_server_blacklisted(interaction.user.id):
            await interaction.response.send_message('This server is blacklisted and you cannot use any commands', ephemeral=True)
            return
        if not interaction.user.guild_permissions.manage_channels : 
            await interaction.response.send_message("You dont have the right permission to lock the channel", ephemeral=True)
            return
        if not interaction.guild.me.guild_permissions.manage_channels :
            await interaction.response.send_message("I dont have manage channels permissions to lock the channel", ephemeral=True)
            return
        channel = interaction.channel
        everyone_role = interaction.guild.default_role

        # Enable @everyone to send messages
        await channel.set_permissions(everyone_role, send_messages=True)

        embed = discord.Embed(
            title="Channel Unlocked",
            description=f"The channel {channel.mention} has been unlocked. @everyone can now send messages.",
            color=discord.Color.green()
        )
        embed.set_footer(
            text=f"Unlocked by {interaction.user}",
            icon_url=interaction.user.display_avatar.url
        )
        embed.timestamp = discord.utils.utcnow()

        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(LockCommand(bot))
