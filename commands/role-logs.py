import discord
from discord import app_commands
from discord.ext import commands
import json
import os

class RoleLogCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.role_log_channels = self.load_log_channels()

    def load_log_channels(self):
        if os.path.exists('rolelog_channels.json'):
            with open('rolelog_channels.json', 'r') as f:
                return json.load(f)
        else:
            return {}

    def save_log_channels(self):
        with open('rolelog_channels.json', 'w') as f:
            json.dump(self.role_log_channels, f, indent=4)

    async def log_role_event(self, guild_id, description, color=discord.Color.blue()):
        if guild_id in self.role_log_channels:
            log_channel_id = self.role_log_channels[guild_id]
            log_channel = self.bot.get_channel(log_channel_id)
            if log_channel:
                embed = discord.Embed(
                    description=description,
                    color=color
                )
                embed.timestamp = discord.utils.utcnow()
                await log_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_role_create(self, role):
        description = f"Role created: {role.mention} ({role.name})"
        await self.log_role_event(str(role.guild.id), description, discord.Color.green())

    @commands.Cog.listener()
    async def on_guild_role_delete(self, role):
        description = f"Role deleted: {role.name}"
        await self.log_role_event(str(role.guild.id), description, discord.Color.red())

    @commands.Cog.listener()
    async def on_guild_role_update(self, before, after):
        changes = []
        if before.name != after.name:
            changes.append(f"Name changed: {before.name} -> {after.name}")
        if before.permissions != after.permissions:
            changes.append(f"Permissions changed: {before.permissions} -> {after.permissions}")
        if changes:
            description = f"Role updated: {after.mention} ({after.name})\n" + "\n".join(changes)
            await self.log_role_event(str(after.guild.id), description, discord.Color.orange())

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        if before.roles != after.roles:
            added_roles = [role for role in after.roles if role not in before.roles]
            removed_roles = [role for role in before.roles if role not in after.roles]
            if added_roles:
                for role in added_roles:
                    description = f"Role {role.mention} ({role.name}) given to {after.mention}"
                    await self.log_role_event(str(after.guild.id), description, discord.Color.green())
            if removed_roles:
                for role in removed_roles:
                    description = f"Role {role.mention} ({role.name}) removed from {after.mention}"
                    await self.log_role_event(str(after.guild.id), description, discord.Color.red())

    @app_commands.command(name="set-role-log", description="Sets the channel where role actions will be logged")
    @app_commands.describe(channel="The channel to log role actions")
    async def set_role_log(self, interaction: discord.Interaction, channel: discord.TextChannel):
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
        self.role_log_channels[guild_id] = channel.id
        self.save_log_channels()

        await interaction.response.send_message(f"Role log channel set to {channel.mention}", ephemeral=True)

    @app_commands.command(name="disable-role-log", description="Disables role logging for the server")
    async def disable_role_log(self, interaction: discord.Interaction):
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
        if guild_id in self.role_log_channels:
            del self.role_log_channels[guild_id]
            self.save_log_channels()
            await interaction.response.send_message("Role log channel has been disabled.", ephemeral=True)
        else:
            await interaction.response.send_message("Role log channel is not set.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(RoleLogCommand(bot))
