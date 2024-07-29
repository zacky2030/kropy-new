import discord
from discord import app_commands
from discord.ext import commands
import datetime
import json
import os

class WarnCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.warns = self.load_warns()
        self.log_channels = self.load_log_channels()

    def load_warns(self):
        if os.path.exists('warnlogs.json'):
            with open('warnlogs.json', 'r') as f:
                return json.load(f)
        else:
            return {}

    def save_warns(self):
        with open('warnlogs.json', 'w') as f:
            json.dump(self.warns, f, indent=4)

    def load_log_channels(self):
        if os.path.exists('log_channels.json'):
            with open('log_channels.json', 'r') as f:
                return json.load(f)
        else:
            return {}

    def save_log_channels(self):
        with open('log_channels.json', 'w') as f:
            json.dump(self.log_channels, f, indent=4)

    @app_commands.command(name="warn", description="Warns a user and logs the warning")
    @app_commands.describe(user="The user to warn", reason="Reason for the warning")
    async def warn(self, interaction: discord.Interaction, user: discord.User, reason: str = "No reason provided"):
        from bot import is_user_blacklisted, is_server_blacklisted  # Import the helper functions
        if is_user_blacklisted(interaction.user.id):
            await interaction.response.send_message("You r blacklisted and cannot use any commands.", ephemeral=True)
            return       
        if is_server_blacklisted(interaction.user.id):
            await interaction.response.send_message('This server is blacklisted and you cannot use any commands', ephemeral=True)
            return
        if not interaction.guild.me.guild_permissions.moderate_members:
            await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)
            return
        if not interaction.user.guild_permissions.manage_messages:
            await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)
            return

        guild_id = str(interaction.guild_id)
        user_id = str(user.id)
        if guild_id not in self.warns:
            self.warns[guild_id] = {}
        if user_id not in self.warns[guild_id]:
            self.warns[guild_id][user_id] = []

        self.warns[guild_id][user_id].append(reason)
        self.save_warns()

        # Send warning message
        embed = discord.Embed(
            title="User Warned",
            description=f"{user.mention} has been warned.\nReason: {reason}\nTotal Warnings: {len(self.warns[guild_id][user_id])}",
            color=discord.Color.orange()
        )
        embed.set_footer(
            text=f"Warned by {interaction.user}",
            icon_url=interaction.user.display_avatar.url
        )
        embed.timestamp = discord.utils.utcnow()

        await interaction.response.send_message(embed=embed)

        # Log the warning
        if guild_id in self.log_channels:
            log_channel_id = self.log_channels[guild_id]
            log_channel = interaction.guild.get_channel(log_channel_id)
            if log_channel:
                await log_channel.send(embed=embed)

        # Check if user has 3 warnings
        if len(self.warns[guild_id][user_id]) >= 3:
            member = interaction.guild.get_member(user.id)
            if member:
                timeout_duration = 300  # 5 minutes in seconds
                try:
                    await member.edit(timed_out_until=discord.utils.utcnow() + datetime.timedelta(seconds=timeout_duration))
                    await interaction.channel.send(f"{user.mention} has been timed out for 5 minutes due to 3 warnings.")
                except discord.Forbidden:
                    await interaction.channel.send(f"Failed to timeout {user.mention} due to insufficient permissions.")
                self.warns[guild_id][user_id] = []  # Reset warnings after timeout
                self.save_warns()

    @app_commands.command(name="warn-remove", description="Removes a warning from a user")
    @app_commands.describe(user="The user to remove a warning from", index="The index of the warning to remove (starting from 1)")
    async def warn_remove(self, interaction: discord.Interaction, user: discord.User, index: int):
        from bot import is_user_blacklisted, is_server_blacklisted  # Import the helper functions
        if is_user_blacklisted(interaction.user.id):
            await interaction.response.send_message("You r blacklisted and cannot use any commands.", ephemeral=True)
            return       
        if is_server_blacklisted(interaction.user.id):
            await interaction.response.send_message('This server is blacklisted and you cannot use any commands', ephemeral=True)
            return
        if not interaction.guild.me.guild_permissions.moderate_members:
            await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)
            return
        if not interaction.user.guild_permissions.manage_messages:
            await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)
            return

        guild_id = str(interaction.guild_id)
        user_id = str(user.id)
        if guild_id not in self.warns or user_id not in self.warns[guild_id] or len(self.warns[guild_id][user_id]) < index or index <= 0:
            await interaction.response.send_message("Invalid warning index.", ephemeral=True)
            return

        del self.warns[guild_id][user_id][index - 1]
        self.save_warns()

        embed = discord.Embed(
            title="Warning Removed",
            description=f"Removed warning {index} from {user.mention}.",
            color=discord.Color.green()
        )
        embed.set_footer(
            text=f"Removed by {interaction.user}",
            icon_url=interaction.user.display_avatar.url
        )
        embed.timestamp = discord.utils.utcnow()

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="setwarnlog", description="Sets the channel where warnings will be logged")
    @app_commands.describe(channel="The channel to log warnings")
    async def setwarnlog(self, interaction: discord.Interaction, channel: discord.TextChannel):
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
        if not interaction.guild.me.guild_permissions.manage_channels:
            await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)
            return

        guild_id = str(interaction.guild_id)
        self.log_channels[guild_id] = channel.id
        self.save_log_channels()

        await interaction.response.send_message(f"Warning log channel set to {channel.mention}", ephemeral=True)

    @app_commands.command(name="disable-warn-log", description="Disables warning logging for the server")
    async def disable_warn_log(self, interaction: discord.Interaction):
        from bot import is_user_blacklisted, is_server_blacklisted  # Import the helper functions
        if is_user_blacklisted(interaction.user.id):
            await interaction.response.send_message("You r blacklisted and cannot use any commands.", ephemeral=True)
            return       
        if is_server_blacklisted(interaction.user.id):
            await interaction.response.send_message('This server is blacklisted and you cannot use any commands', ephemeral=True)
            return
        if not interaction.guild.me.guild_permissions.manage_channels:
            await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)
            return
        if not interaction.user.guild_permissions.manage_guild:
            await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)
            return

        guild_id = str(interaction.guild_id)
        if guild_id in self.log_channels:
            del self.log_channels[guild_id]
            self.save_log_channels()
            await interaction.response.send_message("Warning log channel has been disabled.", ephemeral=True)
        else:
            await interaction.response.send_message("Warning log channel is not set.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(WarnCommand(bot))
