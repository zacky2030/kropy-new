import discord
from discord.ext import commands
import json
import os

class JoinLeaveLogs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.log_file = 'logs.json'
        if not os.path.exists(self.log_file):
            with open(self.log_file, 'w') as f:
                json.dump({}, f)

    def load_logs(self):
        with open(self.log_file, 'r') as f:
            return json.load(f)

    def save_logs(self, logs):
        with open(self.log_file, 'w') as f:
            json.dump(logs, f, indent=4)

    @discord.app_commands.command(name="set-join-log", description="Set the channel for join logs.")
    async def set_join_log(self, interaction: discord.Interaction, channel: discord.TextChannel):
        from bot import is_user_blacklisted, is_server_blacklisted  # Import the helper functions
        if is_user_blacklisted(interaction.user.id):
            await interaction.response.send_message("You r blacklisted and cannot use any commands.", ephemeral=True)
            return       
        if is_server_blacklisted(interaction.user.id):
            await interaction.response.send_message('This server is blacklisted and you cannot use any commands', ephemeral=True)
            return
        if not interaction.user.guild_permissions.manage_guild:
            await interaction.response.send_message("Sorry, you don't have the right permissions to use this command.", ephemeral=True)
            return

        if not interaction.guild.me.guild_permissions.view_audit_log:
            await interaction.response.send_message("Sorry, I need manage guild permissions to do this command.", ephemeral=True)
            return
        logs = self.load_logs()
        if str(interaction.guild_id) not in logs:
            logs[str(interaction.guild_id)] = {}
        logs[str(interaction.guild_id)]["join_channel"] = channel.id
        self.save_logs(logs)
        await interaction.response.send_message(f"Join log channel set to {channel.mention} for this server.")

    @discord.app_commands.command(name="set-leave-log", description="Set the channel for leave logs.")
    async def set_leave_log(self, interaction: discord.Interaction, channel: discord.TextChannel):
        from bot import is_user_blacklisted, is_server_blacklisted  # Import the helper functions
        if is_user_blacklisted(interaction.user.id):
            await interaction.response.send_message("You r blacklisted and cannot use any commands.", ephemeral=True)
            return       
        if is_server_blacklisted(interaction.user.id):
            await interaction.response.send_message('This server is blacklisted and you cannot use any commands', ephemeral=True)
            return
        if not interaction.user.guild_permissions.manage_guild:
            await interaction.response.send_message("Sorry, you don't have the right permissions to use this command.", ephemeral=True)
            return

        if not interaction.guild.me.guild_permissions.manage_guild:
            await interaction.response.send_message("Sorry, I need manage guild permissions to do this command.", ephemeral=True)
            return
        logs = self.load_logs()
        if str(interaction.guild_id) not in logs:
            logs[str(interaction.guild_id)] = {}
        logs[str(interaction.guild_id)]["leave_channel"] = channel.id
        self.save_logs(logs)
        await interaction.response.send_message(f"Leave log channel set to {channel.mention} for this server.")



    @discord.app_commands.command(name="delete-join-log", description="Delete the join log system.")
    async def delete_join_log(self, interaction: discord.Interaction):
        from bot import is_user_blacklisted, is_server_blacklisted  # Import the helper functions
        if is_user_blacklisted(interaction.user.id):
            await interaction.response.send_message("You r blacklisted and cannot use any commands.", ephemeral=True)
            return       
        if is_server_blacklisted(interaction.user.id):
            await interaction.response.send_message('This server is blacklisted and you cannot use any commands', ephemeral=True)
            return
        if not interaction.user.guild_permissions.manage_guild:
            await interaction.response.send_message("Sorry, you don't have the right permissions to use this command.", ephemeral=True)
            return

        if not interaction.guild.me.guild_permissions.manage_guild:
            await interaction.response.send_message("Sorry, I need manage guild permissions to do this command.", ephemeral=True)
            return
        logs = self.load_logs()
        if str(interaction.guild_id) in logs and "join_channel" in logs[str(interaction.guild_id)]:
            del logs[str(interaction.guild_id)]["join_channel"]
            self.save_logs(logs)
            await interaction.response.send_message("Join log channel has been deleted for this server.")
        else:
            await interaction.response.send_message("No join log channel is set for this server.", ephemeral=True)

    @discord.app_commands.command(name="delete-leave-log", description="Delete the leave log system.")
    async def delete_leave_log(self, interaction: discord.Interaction):
        from bot import is_user_blacklisted, is_server_blacklisted  # Import the helper functions
        if is_user_blacklisted(interaction.user.id):
            await interaction.response.send_message("You r blacklisted and cannot use any commands.", ephemeral=True)
            return       
        if is_server_blacklisted(interaction.user.id):
            await interaction.response.send_message('This server is blacklisted and you cannot use any commands', ephemeral=True)
            return
        if not interaction.user.guild_permissions.manage_guild:
            await interaction.response.send_message("Sorry, you don't have the right permissions to use this command.", ephemeral=True)
            return

        if not interaction.guild.me.guild_permissions.manage_guild:
            await interaction.response.send_message("Sorry, I need manage guild permissions to do this command.", ephemeral=True)
            return
        logs = self.load_logs()
        if str(interaction.guild_id) in logs and "leave_channel" in logs[str(interaction.guild_id)]:
            del logs[str(interaction.guild_id)]["leave_channel"]
            self.save_logs(logs)
            await interaction.response.send_message("Leave log channel has been deleted for this server.")
        else:
            await interaction.response.send_message("No leave log channel is set for this server.", ephemeral=True)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        logs = self.load_logs()
        guild_logs = logs.get(str(member.guild.id), {})
        channel_id = guild_logs.get("join_channel")
        if channel_id:
            channel = self.bot.get_channel(channel_id)
            if channel:
                await channel.send(f"{member.mention} Joined the server, welcome! {member.guild.name} now has {member.guild.member_count} members!")

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        logs = self.load_logs()
        guild_logs = logs.get(str(member.guild.id), {})
        channel_id = guild_logs.get("leave_channel")
        if channel_id:
            channel = self.bot.get_channel(channel_id)
            if channel:
                await channel.send(f"{member.mention} Left the server, goodbye! {member.guild.name} now has {member.guild.member_count} members!")

async def setup(bot):
    await bot.add_cog(JoinLeaveLogs(bot))
