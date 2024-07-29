import discord
from discord.ext import commands
import json
import os

class UserActivityLogs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.log_file = 'user_activity_logs.json'
        if not os.path.exists(self.log_file):
            with open(self.log_file, 'w') as f:
                json.dump({}, f)

    def load_logs(self):
        with open(self.log_file, 'r') as f:
            return json.load(f)

    def save_logs(self, logs):
        with open(self.log_file, 'w') as f:
            json.dump(logs, f, indent=4)

    @discord.app_commands.command(name="set-user-activity-log", description="Set the channel for user activity logs.")
    async def set_user_activity_log(self, interaction: discord.Interaction, channel: discord.TextChannel):
        from bot import is_user_blacklisted, is_server_blacklisted  # Import the helper functions
        if is_user_blacklisted(interaction.user.id):
            await interaction.response.send_message("You r blacklisted and cannot use any commands.", ephemeral=True)
            return       
        if is_server_blacklisted(interaction.user.id):
            await interaction.response.send_message('This server is blacklisted and you cannot use any commands', ephemeral=True)
            return
        if not interaction.user.guild_permissions.manage_channels :
            await interaction.response.send_message("You dont have the right permissions use this command")

        if not interaction.guild.me.guild_permissions.view_audit_log :
            await interaction.response.send_message("i dont have the right permissions use this command")
        logs = self.load_logs()
        logs[str(interaction.guild_id)] = channel.id
        self.save_logs(logs)
        await interaction.response.send_message(f"User activity log channel set to {channel.mention} for this server.")
        print(f"User activity log channel set to {channel.id} for guild {interaction.guild_id}")

    @discord.app_commands.command(name="disable-user-activity-log", description="Disable the user activity log system.")
    async def disable_user_activity_log(self, interaction: discord.Interaction):
        from bot import is_user_blacklisted, is_server_blacklisted  # Import the helper functions
        if is_user_blacklisted(interaction.user.id):
            await interaction.response.send_message("You r blacklisted and cannot use any commands.", ephemeral=True)
            return       
        if is_server_blacklisted(interaction.user.id):
            await interaction.response.send_message('This server is blacklisted and you cannot use any commands', ephemeral=True)
            return
        if not interaction.user.guild_permissions.manage_channels :
            await interaction.response.send_message("You dont have the right permissions use this command")

        if not interaction.guild.me.guild_permissions.view_audit_log :
            await interaction.response.send_message("i dont have the right permissions use this command")
        logs = self.load_logs()
        if str(interaction.guild_id) in logs:
            del logs[str(interaction.guild_id)]
            self.save_logs(logs)
            await interaction.response.send_message("User activity log channel has been disabled for this server.")
            print(f"User activity log channel disabled for guild {interaction.guild_id}")
        else:
            await interaction.response.send_message("No user activity log channel is set for this server.", ephemeral=True)

    @commands.Cog.listener()
    async def on_presence_update(self, before, after):
        if before.status != after.status:
            print(f"Status change detected: {before.status} -> {after.status}")
            logs = self.load_logs()
            print(f"Logs loaded: {logs}")
            channel_id = logs.get(str(after.guild.id))
            print(f"Channel ID from logs: {channel_id}")
            if channel_id:
                channel = self.bot.get_channel(channel_id)
                if channel:
                    print(f"Sending status update to channel {channel.id}")
                    await channel.send(f"Status of {after.name} is now {after.status}!")
                else:
                    print(f"Channel with ID {channel_id} not found")
            else:
                print(f"No log channel set for guild {after.guild.id}")

async def setup(bot):
    await bot.add_cog(UserActivityLogs(bot))
    print("[SETUP] UserActivityLogs cog loaded.")
