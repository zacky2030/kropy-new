import discord
from discord import app_commands
from discord.ext import commands
import json
import os

class KickLogCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.kick_log_channels = self.load_log_channels()

    def load_log_channels(self):
        if os.path.exists('kicklog_channels.json'):
            with open('kicklog_channels.json', 'r') as f:
                return json.load(f)
        else:
            return {}

    def save_log_channels(self):
        with open('kicklog_channels.json', 'w') as f:
            json.dump(self.kick_log_channels, f, indent=4)

    async def log_kick(self, guild_id, user, executor, time):
        if guild_id in self.kick_log_channels:
            log_channel_id = self.kick_log_channels[guild_id]
            log_channel = self.bot.get_channel(log_channel_id)
            if log_channel:
                embed = discord.Embed(
                    title="User Kicked",
                    description=f"{user.mention} was kicked by {executor.mention} at {time}.",
                    color=discord.Color.orange()
                )
                embed.set_footer(text=f"User ID: {user.id} | Kicked by: {executor}", icon_url=executor.display_avatar.url)
                embed.timestamp = time
                await log_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        async for entry in member.guild.audit_logs(limit=1, action=discord.AuditLogAction.kick):
            if entry.target.id == member.id:
                executor = entry.user
                kick_time = entry.created_at
                await self.log_kick(str(member.guild.id), member, executor, kick_time)

    @app_commands.command(name="set-kick-log", description="Sets the channel where kick actions will be logged")
    @app_commands.describe(channel="The channel to log kick actions")
    async def set_kick_log(self, interaction: discord.Interaction, channel: discord.TextChannel):
        from bot import is_user_blacklisted, is_server_blacklisted  # Import the helper functions
        if is_user_blacklisted(interaction.user.id):
            await interaction.response.send_message("You r blacklisted and cannot use any commands.", ephemeral=True)
            return       
        if is_server_blacklisted(interaction.user.id):
            await interaction.response.send_message('This server is blacklisted and you cannot use any commands', ephemeral=True)
            return
        if not interaction.user.guild_permissions.manage_guild:
            await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)
            return
        if not interaction.guild.me.guild_permissions.view_audit_log:
            await interaction.response.send_message("I don't have permission to use this command.", ephemeral=True)
            return
        guild_id = str(interaction.guild_id)
        self.kick_log_channels[guild_id] = channel.id
        self.save_log_channels()

        await interaction.response.send_message(f"Kick log channel set to {channel.mention}", ephemeral=True)

    @app_commands.command(name="disable-kick-log", description="Disables kick logging for the server")
    async def disable_kick_log(self, interaction: discord.Interaction):
        from bot import is_user_blacklisted, is_server_blacklisted  # Import the helper functions
        if is_user_blacklisted(interaction.user.id):
            await interaction.response.send_message("You r blacklisted and cannot use any commands.", ephemeral=True)
            return       
        if is_server_blacklisted(interaction.user.id):
            await interaction.response.send_message('This server is blacklisted and you cannot use any commands', ephemeral=True)
            return
        if not interaction.user.guild_permissions.manage_guild:
            await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)
            return
        if not interaction.guild.me.guild_permissions.view_audit_log:
            await interaction.response.send_message("I don't have permission to use this command.", ephemeral=True)
            return

        guild_id = str(interaction.guild_id)
        if guild_id in self.kick_log_channels:
            del self.kick_log_channels[guild_id]
            self.save_log_channels()
            await interaction.response.send_message("Kick log channel has been disabled.", ephemeral=True)
        else:
            await interaction.response.send_message("Kick log channel is not set.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(KickLogCommand(bot))
