import discord
from discord import app_commands
from discord.ext import commands
import json
import os

class VoiceModerationCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.log_channels = self.load_log_channels()

    def load_log_channels(self):
        if os.path.exists('voicelog_channels.json'):
            with open('voicelog_channels.json', 'r') as f:
                return json.load(f)
        else:
            return {}

    def save_log_channels(self):
        with open('voicelog_channels.json', 'w') as f:
            json.dump(self.log_channels, f, indent=4)

    async def log_action(self, guild_id, message):
        if guild_id in self.log_channels:
            log_channel_id = self.log_channels[guild_id]
            log_channel = self.bot.get_channel(log_channel_id)
            if log_channel:
                await log_channel.send(message)

    @app_commands.command(name="vkick", description="Kicks a member from the voice channel the user is currently in")
    @app_commands.describe(member="The member to kick from the voice channel")
    async def vkick(self, interaction: discord.Interaction, member: discord.Member):
        from bot import is_user_blacklisted, is_server_blacklisted  # Import the helper functions
        if is_user_blacklisted(interaction.user.id):
            await interaction.response.send_message("You r blacklisted and cannot use any commands.", ephemeral=True)
            return       
        if is_server_blacklisted(interaction.user.id):
            await interaction.response.send_message('This server is blacklisted and you cannot use any commands', ephemeral=True)
            return
        if not interaction.user.guild_permissions.move_members:
            await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)
            return
        if not interaction.guild.me.guild_permissions.move_members:
            await interaction.response.send_message("I don't have permission to use this command.", ephemeral=True)
            return

        if interaction.user.voice is None or interaction.user.voice.channel is None:
            await interaction.response.send_message("You are not in a voice channel.", ephemeral=True)
            return

        voice_channel = interaction.user.voice.channel
        if member.voice and member.voice.channel == voice_channel:
            await member.move_to(None)
            await interaction.response.send_message(f"{member.mention} has been kicked from the voice channel.", ephemeral=True)
            await self.log_action(str(interaction.guild_id), f"{member.mention} was kicked from {voice_channel.mention} by {interaction.user.mention}.")
        else:
            await interaction.response.send_message(f"{member.mention} is not in your voice channel.", ephemeral=True)

    @app_commands.command(name="vmute", description="Mutes a member in voice channels")
    @app_commands.describe(member="The member to mute in voice channels")
    async def vmute(self, interaction: discord.Interaction, member: discord.Member):
        from bot import is_user_blacklisted, is_server_blacklisted  # Import the helper functions
        if is_user_blacklisted(interaction.user.id):
            await interaction.response.send_message("You r blacklisted and cannot use any commands.", ephemeral=True)
            return       
        if is_server_blacklisted(interaction.user.id):
            await interaction.response.send_message('This server is blacklisted and you cannot use any commands', ephemeral=True)
            return
        if not interaction.user.guild_permissions.mute_members:
            await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)
            return
        if not interaction.guild.me.guild_permissions.mute_members:
            await interaction.response.send_message("I don't have permission to use this command.", ephemeral=True)
            return

        await member.edit(mute=True)
        await interaction.response.send_message(f"{member.mention} has been muted in voice channels.", ephemeral=True)
        await self.log_action(str(interaction.guild_id), f"{member.mention} was muted by {interaction.user.mention}.")

    @app_commands.command(name="vunmute", description="Unmutes a member in voice channels")
    @app_commands.describe(member="The member to unmute in voice channels")
    async def vunmute(self, interaction: discord.Interaction, member: discord.Member):
        from bot import is_user_blacklisted, is_server_blacklisted  # Import the helper functions
        if is_user_blacklisted(interaction.user.id):
            await interaction.response.send_message("You r blacklisted and cannot use any commands.", ephemeral=True)
            return       
        if is_server_blacklisted(interaction.user.id):
            await interaction.response.send_message('This server is blacklisted and you cannot use any commands', ephemeral=True)
            return
        if not interaction.user.guild_permissions.mute_members:
            await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)
            return
        if not interaction.guild.me.guild_permissions.mute_members:
            await interaction.response.send_message("I don't have permission to use this command.", ephemeral=True)
            return
        await member.edit(mute=False)
        await interaction.response.send_message(f"{member.mention} has been unmuted in voice channels.", ephemeral=True)
        await self.log_action(str(interaction.guild_id), f"{member.mention} was unmuted by {interaction.user.mention}.")

    @app_commands.command(name="vdeafen", description="Deafens a member in voice channels")
    @app_commands.describe(member="The member to deafen in voice channels")
    async def vdeafen(self, interaction: discord.Interaction, member: discord.Member):
        from bot import is_user_blacklisted, is_server_blacklisted  # Import the helper functions
        if is_user_blacklisted(interaction.user.id):
            await interaction.response.send_message("You r blacklisted and cannot use any commands.", ephemeral=True)
            return       
        if is_server_blacklisted(interaction.user.id):
            await interaction.response.send_message('This server is blacklisted and you cannot use any commands', ephemeral=True)
            return
        if not interaction.user.guild_permissions.deafen_members:
            await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)
            return
        
        if not interaction.guild.me.guild_permissions.deafen_members:
            await interaction.response.send_message("I don't have permission to use this command.", ephemeral=True)
            return

        await member.edit(deafen=True)
        await interaction.response.send_message(f"{member.mention} has been deafened in voice channels.", ephemeral=True)
        await self.log_action(str(interaction.guild_id), f"{member.mention} was deafened by {interaction.user.mention}.")

    @app_commands.command(name="vundeafen", description="Removes the deafen status from a member")
    @app_commands.describe(member="The member to undeafen in voice channels")
    async def vundeafen(self, interaction: discord.Interaction, member: discord.Member):
        from bot import is_user_blacklisted, is_server_blacklisted  # Import the helper functions
        if is_user_blacklisted(interaction.user.id):
            await interaction.response.send_message("You r blacklisted and cannot use any commands.", ephemeral=True)
            return       
        if is_server_blacklisted(interaction.user.id):
            await interaction.response.send_message('This server is blacklisted and you cannot use any commands', ephemeral=True)
            return
        if not interaction.user.guild_permissions.deafen_members:
            await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)
            return
        if not interaction.guild.me.guild_permissions.deafen_members:
            await interaction.response.send_message("I don't have permission to use this command.", ephemeral=True)
            return

        await member.edit(deafen=False)
        await interaction.response.send_message(f"{member.mention} has been undeafened in voice channels.", ephemeral=True)
        await self.log_action(str(interaction.guild_id), f"{member.mention} was undeafened by {interaction.user.mention}.")

    @app_commands.command(name="vmoveme", description="Moves you to another voice channel")
    @app_commands.describe(channel="The voice channel to move to")
    async def vmoveme(self, interaction: discord.Interaction, channel: discord.VoiceChannel):
        from bot import is_user_blacklisted, is_server_blacklisted  # Import the helper functions
        if is_user_blacklisted(interaction.user.id):
            await interaction.response.send_message("You r blacklisted and cannot use any commands.", ephemeral=True)
            return       
        if is_server_blacklisted(interaction.user.id):
            await interaction.response.send_message('This server is blacklisted and you cannot use any commands', ephemeral=True)
            return
        if interaction.user.voice is None or interaction.user.voice.channel is None:
            await interaction.response.send_message("You are not in a voice channel.", ephemeral=True)
            return
        if not interaction.guild.me.guild_permissions.move_members:
            await interaction.response.send_message("I don't have permission to use this command.", ephemeral=True)
            return
        
        if not interaction.user.guild_permissions.move_members:
            await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)
            return

        await interaction.user.move_to(channel)
        await interaction.response.send_message(f"You have been moved to {channel.mention}.", ephemeral=True)
        await self.log_action(str(interaction.guild_id), f"{interaction.user.mention} moved to {channel.mention}.")

    @app_commands.command(name="vmove", description="Moves a member to another voice channel")
    @app_commands.describe(member="The member to move", channel="The voice channel to move to")
    async def vmove(self, interaction: discord.Interaction, member: discord.Member, channel: discord.VoiceChannel):
        from bot import is_user_blacklisted, is_server_blacklisted  # Import the helper functions
        if is_user_blacklisted(interaction.user.id):
            await interaction.response.send_message("You r blacklisted and cannot use any commands.", ephemeral=True)
            return       
        if is_server_blacklisted(interaction.user.id):
            await interaction.response.send_message('This server is blacklisted and you cannot use any commands', ephemeral=True)
            return
        if not interaction.user.guild_permissions.move_members:
            await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)
            return
        
        if not interaction.guild.me.guild_permissions.move_members:
            await interaction.response.send_message("I don't have permission to use this command.", ephemeral=True)
            return
        if member.voice is None or member.voice.channel is None:
            await interaction.response.send_message(f"{member.mention} is not in a voice channel.", ephemeral=True)
            return

        await member.move_to(channel)
        await interaction.response.send_message(f"{member.mention} has been moved to {channel.mention}.", ephemeral=True)
        await self.log_action(str(interaction.guild_id), f"{member.mention} was moved to {channel.mention} by {interaction.user.mention}.")

    @app_commands.command(name="voicelog-set", description="Sets the channel where voice moderation actions will be logged")
    @app_commands.describe(channel="The channel to log voice moderation actions")
    async def voicelog_set(self, interaction: discord.Interaction, channel: discord.TextChannel):
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
        self.log_channels[guild_id] = channel.id
        self.save_log_channels()

        await interaction.response.send_message(f"Voice moderation log channel set to {channel.mention}", ephemeral=True)

    @app_commands.command(name="voicelog-disable", description="Disables voice moderation logging for the server")
    async def voicelog_disable(self, interaction: discord.Interaction):
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
        if guild_id in self.log_channels:
            del self.log_channels[guild_id]
            self.save_log_channels()
            await interaction.response.send_message("Voice moderation log channel has been disabled.", ephemeral=True)
        else:
            await interaction.response.send_message("Voice moderation log channel is not set.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(VoiceModerationCommand(bot))
