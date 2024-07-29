import discord
from discord.ext import commands
import json
import os

class MessageLogs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config_file = 'message_logs.json'
        if not os.path.exists(self.config_file):
            with open(self.config_file, 'w') as f:
                json.dump({}, f)
        self.message_logs = self.load_message_logs()

    def load_message_logs(self):
        with open(self.config_file, 'r') as f:
            return json.load(f)

    def save_message_logs(self):
        with open(self.config_file, 'w') as f:
            json.dump(self.message_logs, f, indent=4)

    @discord.app_commands.command(name="set-message-log", description="Set the channel for message logs.")
    async def set_message_logs(self, interaction: discord.Interaction, channel: discord.TextChannel):
        from bot import is_user_blacklisted, is_server_blacklisted  # Import the helper functions
        if is_user_blacklisted(interaction.user.id):
            await interaction.response.send_message("You r blacklisted and cannot use any commands.", ephemeral=True)
            return       
        if is_server_blacklisted(interaction.user.id):
            await interaction.response.send_message('This server is blacklisted and you cannot use any commands', ephemeral=True)
            return
        if not interaction.user.guild_permissions.manage_channels:
            await interaction.response.send_message("Sorry, you don't have the right permissions to use this command.", ephemeral=True)
            return

        if not interaction.guild.me.guild_permissions.manage_channels:
            await interaction.response.send_message("Sorry, I need manage channels permissions to do this command.", ephemeral=True)
            return
        
        guild_id = str(interaction.guild_id)
        self.message_logs[guild_id] = {
            "channel_id": channel.id
        }
        self.save_message_logs()
        await interaction.response.send_message(f"Message logs channel set to {channel.mention} for this server.")

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if before.author.bot:
            return
        
        guild_id = str(before.guild.id)
        if guild_id not in self.message_logs:
            return

        log_channel_id = self.message_logs[guild_id]["channel_id"]
        log_channel = self.bot.get_channel(log_channel_id)
        if log_channel:
            embed = discord.Embed(title="Message Edited", color=discord.Color.orange())
            embed.add_field(name="Before", value=before.content, inline=False)
            embed.add_field(name="After", value=after.content, inline=False)
            embed.set_footer(text=f"Author: {before.author} | Message ID: {before.id}")
            await log_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.author.bot:
            return

        guild_id = str(message.guild.id)
        if guild_id not in self.message_logs:
            return

        log_channel_id = self.message_logs[guild_id]["channel_id"]
        log_channel = self.bot.get_channel(log_channel_id)
        if log_channel:
            embed = discord.Embed(title="Message Deleted", color=discord.Color.red())
            embed.add_field(name="Content", value=message.content, inline=False)
            embed.set_footer(text=f"Author: {message.author} | Message ID: {message.id}")
            await log_channel.send(embed=embed)

async def setup(bot):
    await bot.add_cog(MessageLogs(bot))
