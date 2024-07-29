import discord
from discord import app_commands
from discord.ext import commands
import json
import os

class BanLogCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.ban_log_channels = self.load_log_channels('banlog_channels.json')
        self.unban_log_channels = self.load_log_channels('unbanlog_channels.json')

    def load_log_channels(self, filename):
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                return json.load(f)
        else:
            return {}

    def save_log_channels(self, channels, filename):
        with open(filename, 'w') as f:
            json.dump(channels, f, indent=4)

    async def log_action(self, guild_id, user, executor, time, action_type):
        if action_type == "ban":
            log_channels = self.ban_log_channels
            color = discord.Color.red()
            title = "User Banned"
            description = f"{user.mention} was banned by {executor.mention} at {time}."
        elif action_type == "unban":
            log_channels = self.unban_log_channels
            color = discord.Color.green()
            title = "User Unbanned"
            description = f"{user.mention} was unbanned by {executor.mention} at {time}."
        
        if guild_id in log_channels:
            log_channel_id = log_channels[guild_id]
            log_channel = self.bot.get_channel(log_channel_id)
            if log_channel:
                embed = discord.Embed(
                    title=title,
                    description=description,
                    color=color
                )
                embed.set_footer(text=f"User ID: {user.id} | {action_type.capitalize()} by: {executor}", icon_url=executor.display_avatar.url)
                embed.timestamp = time
                await log_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
        async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.ban):
            executor = entry.user
            ban_time = entry.created_at
            await self.log_action(str(guild.id), user, executor, ban_time, "ban")

    @commands.Cog.listener()
    async def on_member_unban(self, guild, user):
        async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.unban):
            executor = entry.user
            unban_time = entry.created_at
            await self.log_action(str(guild.id), user, executor, unban_time, "unban")

    @app_commands.command(name="set-ban-log", description="Sets the channel where ban actions will be logged")
    @app_commands.describe(channel="The channel to log ban actions")
    async def set_ban_log(self, interaction: discord.Interaction, channel: discord.TextChannel):
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
        self.ban_log_channels[guild_id] = channel.id
        self.save_log_channels(self.ban_log_channels, 'banlog_channels.json')

        await interaction.response.send_message(f"Ban log channel set to {channel.mention}", ephemeral=True)

    @app_commands.command(name="disable-ban-log", description="Disables ban logging for the server")
    async def disable_ban_log(self, interaction: discord.Interaction):
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
        if guild_id in self.ban_log_channels:
            del self.ban_log_channels[guild_id]
            self.save_log_channels(self.ban_log_channels, 'banlog_channels.json')
            await interaction.response.send_message("Ban log channel has been disabled.", ephemeral=True)
        else:
            await interaction.response.send_message("Ban log channel is not set.", ephemeral=True)

    @app_commands.command(name="set-unban-log", description="Sets the channel where unban actions will be logged")
    @app_commands.describe(channel="The channel to log unban actions")
    async def set_unban_log(self, interaction: discord.Interaction, channel: discord.TextChannel):
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
        if not interaction.guild.me.guild_permissions.manage_guild:
            await interaction.response.send_message("I don't have permission to use this command.", ephemeral=True)
            return

        guild_id = str(interaction.guild_id)
        self.unban_log_channels[guild_id] = channel.id
        self.save_log_channels(self.unban_log_channels, 'unbanlog_channels.json')

        await interaction.response.send_message(f"Unban log channel set to {channel.mention}", ephemeral=True)

    @app_commands.command(name="disable-unban-log", description="Disables unban logging for the server")
    async def disable_unban_log(self, interaction: discord.Interaction):
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
        
        if not interaction.guild.me.guild_permissions.manage_guild:
            await interaction.response.send_message("I don't have permission to use this command.", ephemeral=True)
            return

        guild_id = str(interaction.guild_id)
        if guild_id in self.unban_log_channels:
            del self.unban_log_channels[guild_id]
            self.save_log_channels(self.unban_log_channels, 'unbanlog_channels.json')
            await interaction.response.send_message("Unban log channel has been disabled.", ephemeral=True)
        else:
            await interaction.response.send_message("Unban log channel is not set.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(BanLogCommand(bot))
