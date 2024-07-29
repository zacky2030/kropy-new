import discord
from discord.ext import commands
import json
import os

class LevelSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config_file = 'level_system.json'
        if not os.path.exists(self.config_file):
            with open(self.config_file, 'w') as f:
                json.dump({}, f)
        self.levels = self.load_levels()

    def load_levels(self):
        with open(self.config_file, 'r') as f:
            return json.load(f)

    def save_levels(self):
        with open(self.config_file, 'w') as f:
            json.dump(self.levels, f, indent=4)

    def get_xp_required(self, level):
        return 5000 + (level - 1) * 2500

    @discord.app_commands.command(name="set-level-log", description="Set the channel for level logs.")
    async def set_level_log(self, interaction: discord.Interaction, channel: discord.TextChannel):
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
        if guild_id not in self.levels:
            self.levels[guild_id] = {"enabled": True, "log_channel": channel.id, "users": {}}
        else:
            self.levels[guild_id]["log_channel"] = channel.id
        self.save_levels()
        await interaction.response.send_message(f"Level log channel set to {channel.mention} for this server.")

    @discord.app_commands.command(name="disable-level-system", description="Disable the level system.")
    async def disable_level_system(self, interaction: discord.Interaction):
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
        if guild_id in self.levels:
            self.levels[guild_id]["enabled"] = False
            self.save_levels()
            await interaction.response.send_message("Level system has been disabled for this server.")
        else:
            await interaction.response.send_message("No level system is set for this server.", ephemeral=True)

    @discord.app_commands.command(name="enable-level-system", description="Enable the level system.")
    async def enable_level_system(self, interaction: discord.Interaction):
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
        if guild_id in self.levels:
            self.levels[guild_id]["enabled"] = True
            self.save_levels()
            await interaction.response.send_message("Level system has been enabled for this server.")
        else:
            await interaction.response.send_message("No level system is set for this server.", ephemeral=True)

    @discord.app_commands.command(name="reset-level-system", description="Reset the level system.")
    async def reset_level_system(self, interaction: discord.Interaction):
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
        if guild_id in self.levels:
            self.levels[guild_id]["users"] = {}
            self.save_levels()
            await interaction.response.send_message("Level system has been reset for this server.")
        else:
            await interaction.response.send_message("No level system is set for this server.", ephemeral=True)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        
        guild_id = str(message.guild.id)
        user_id = str(message.author.id)
        
        if guild_id not in self.levels or not self.levels[guild_id].get("enabled", False):
            return
        
        if user_id not in self.levels[guild_id]["users"]:
            self.levels[guild_id]["users"][user_id] = {"xp": 0, "level": 0}

        user_data = self.levels[guild_id]["users"][user_id]
        user_data["xp"] += 500
        xp_required = self.get_xp_required(user_data["level"] + 1)

        if user_data["xp"] >= xp_required:
            user_data["xp"] -= xp_required
            user_data["level"] += 1
            log_channel_id = self.levels[guild_id]["log_channel"]
            log_channel = self.bot.get_channel(log_channel_id)
            if log_channel:
                await log_channel.send(f"Congrats {message.author.mention}, Now you are level {user_data['level']}!")
        
        self.save_levels()

async def setup(bot):
    await bot.add_cog(LevelSystem(bot))
