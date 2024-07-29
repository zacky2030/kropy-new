import discord
from discord.ext import commands
from discord.ui import Button, View
import json
import os

class TicketSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config_file = 'ticket_system.json'
        if not os.path.exists(self.config_file):
            with open(self.config_file, 'w') as f:
                json.dump({}, f)
        self.ticket_systems = self.load_ticket_systems()
        self.bot.loop.create_task(self._register_existing_buttons())

    def load_ticket_systems(self):
        with open(self.config_file, 'r') as f:
            return json.load(f)

    def save_ticket_systems(self):
        with open(self.config_file, 'w') as f:
            json.dump(self.ticket_systems, f, indent=4)

    async def _register_existing_buttons(self):
        await self.bot.wait_until_ready()
        for guild_id, config in self.ticket_systems.items():
            channel_id = config.get("channel_id")
            message_id = config.get("message_id")
            if channel_id and message_id:
                view = self.create_ticket_view()
                self.bot.add_view(view, message_id=message_id)

    def create_ticket_view(self):
        view = View(timeout=None)  # Ensure the view does not timeout
        button = Button(label="📩 Ticket", style=discord.ButtonStyle.primary, custom_id="create_ticket")
        button.callback = self.create_ticket_callback
        view.add_item(button)
        return view

    @discord.app_commands.command(name="create-ticket-system", description="Create a ticket system in the specified category and channel.")
    async def create_ticket_system(self, interaction: discord.Interaction, category: discord.CategoryChannel, channel: discord.TextChannel, mod_role: discord.Role):
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
            await interaction.response.send_message("Sorry, I don't have the right permissions to do this.", ephemeral=True)
            return

        guild_id = str(interaction.guild_id)
        self.ticket_systems[guild_id] = {
            "category_id": category.id,
            "channel_id": channel.id,
            "mod_role_id": mod_role.id,
            "enabled": True,
            "message_id": None
        }
        self.save_ticket_systems()
        
        embed = discord.Embed(title="Ticket System", description="Click the button below to create a ticket.", color=discord.Color.green())
        view = self.create_ticket_view()
        message = await channel.send(embed=embed, view=view)

        # Save the message ID to delete it later if needed
        self.ticket_systems[guild_id]["message_id"] = message.id
        self.save_ticket_systems()

        await interaction.response.send_message(f"Ticket system created in category {category.name} with channel {channel.mention} and mod role {mod_role.mention}")

    async def create_ticket_callback(self, interaction: discord.Interaction):
        guild_id = str(interaction.guild.id)
        config = self.ticket_systems.get(guild_id)
        if not config or not config.get("enabled"):
            await interaction.response.send_message("Ticket system is disabled.", ephemeral=True)
            return
        
        category = interaction.guild.get_channel(config["category_id"])
        mod_role = interaction.guild.get_role(config["mod_role_id"])

        ticket_channel = await category.create_text_channel(f'ticket-{interaction.user.display_name}')
        await ticket_channel.set_permissions(interaction.guild.default_role, read_messages=False)
        await ticket_channel.set_permissions(interaction.user, read_messages=True, send_messages=True)
        await ticket_channel.set_permissions(mod_role, read_messages=True, send_messages=True)
        
        embed = discord.Embed(title="Ticket", description=f"Ticket created by {interaction.user.mention}.", color=discord.Color.blue())
        view = self.create_ticket_control_view(mod_role.id)

        await ticket_channel.send(embed=embed, view=view)
        await interaction.response.send_message(f'{interaction.user.mention}, your ticket has been created: {ticket_channel.mention}', ephemeral=True)

    def create_ticket_control_view(self, mod_role_id):
        view = View(timeout=None)  # Ensure the view does not timeout

        claim_button = Button(label="Claim Ticket", style=discord.ButtonStyle.success, custom_id="claim_ticket")
        close_button = Button(label="Close Ticket", style=discord.ButtonStyle.danger, custom_id="close_ticket")

        async def claim_ticket(interaction: discord.Interaction):
            if mod_role_id not in [role.id for role in interaction.user.roles]:
                await interaction.response.send_message("You do not have permission to claim this ticket.", ephemeral=True)
                return
            await interaction.channel.set_permissions(interaction.user, send_messages=True)
            await interaction.response.send_message(f"Ticket claimed by {interaction.user.mention}.", ephemeral=True)

        async def close_ticket(interaction: discord.Interaction):
            await interaction.channel.delete()
        
        claim_button.callback = claim_ticket
        close_button.callback = close_ticket

        view.add_item(claim_button)
        view.add_item(close_button)

        return view

    @discord.app_commands.command(name="disable-ticket-system", description="Disable the ticket system.")
    async def disable_ticket_system(self, interaction: discord.Interaction):
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
            await interaction.response.send_message("Sorry, I don't have the right permissions to do this.", ephemeral=True)
            return

        guild_id = str(interaction.guild_id)
        if guild_id in self.ticket_systems:
            self.ticket_systems[guild_id]["enabled"] = False
            self.save_ticket_systems()
            await interaction.response.send_message("Ticket system has been disabled for this server.")
        else:
            await interaction.response.send_message("No ticket system is set for this server.", ephemeral=True)

    @discord.app_commands.command(name="enable-ticket-system", description="Enable the ticket system.")
    async def enable_ticket_system(self, interaction: discord.Interaction):
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
            await interaction.response.send_message("Sorry, I don't have the right permissions to do this.", ephemeral=True)
            return

        guild_id = str(interaction.guild_id)
        if guild_id in self.ticket_systems:
            self.ticket_systems[guild_id]["enabled"] = True
            self.save_ticket_systems()
            await interaction.response.send_message("Ticket system has been enabled for this server.")
        else:
            await interaction.response.send_message("No ticket system is set for this server.", ephemeral=True)

    @discord.app_commands.command(name="ticket-system-delete", description="Delete the ticket system and the setup message.")
    async def ticket_system_delete(self, interaction: discord.Interaction):
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
            await interaction.response.send_message("Sorry, I don't have the right permissions to do this.", ephemeral=True)
            return

        guild_id = str(interaction.guild_id)
        if guild_id in self.ticket_systems:
            channel_id = self.ticket_systems[guild_id]["channel_id"]
            message_id = self.ticket_systems[guild_id]["message_id"]
            channel = interaction.guild.get_channel(channel_id)
            if channel:
                try:
                    message = await channel.fetch_message(message_id)
                    await message.delete()
                except discord.NotFound:
                    pass
            del self.ticket_systems[guild_id]
            self.save_ticket_systems()
            await interaction.response.send_message("Ticket system has been deleted for this server.")
        else:
            await interaction.response.send_message("No ticket system is set for this server.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(TicketSystem(bot))
