import discord
from discord.ext import commands
import json
import os

class AutoRespond(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.file_path = 'auto_respond.json'
        self.responses = self.load_responses()

    def load_responses(self):
        if os.path.exists(self.file_path):
            with open(self.file_path, 'r') as f:
                return json.load(f)
        return {}

    def save_responses(self):
        with open(self.file_path, 'w') as f:
            json.dump(self.responses, f, indent=4)

    def get_server_responses(self, guild_id):
        return self.responses.get(str(guild_id), {})

    def set_server_response(self, guild_id, trigger, response):
        if str(guild_id) not in self.responses:
            self.responses[str(guild_id)] = {}
        self.responses[str(guild_id)][trigger.lower()] = response
        self.save_responses()

    def remove_server_response(self, guild_id, trigger):
        if str(guild_id) in self.responses and trigger.lower() in self.responses[str(guild_id)]:
            del self.responses[str(guild_id)][trigger.lower()]
            if not self.responses[str(guild_id)]:
                del self.responses[str(guild_id)]
            self.save_responses()

    @discord.app_commands.command(name="set-auto-respond", description="Set an auto-response for a trigger.")
    async def auto_respond(self, interaction: discord.Interaction, trigger: str, response: str):
        from bot import is_user_blacklisted, is_server_blacklisted  # Import the helper functions
        if is_user_blacklisted(interaction.user.id):
            await interaction.response.send_message("You r blacklisted and cannot use any commands.", ephemeral=True)
            return       
        if is_server_blacklisted(interaction.user.id):
            await interaction.response.send_message('This server is blacklisted and you cannot use any commands', ephemeral=True)
            return
        if not interaction.user.guild_permissions.manage_messages:
            await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)
            return
        guild_id = interaction.guild_id
        self.set_server_response(guild_id, trigger, response)
        await interaction.response.send_message(f"Auto-response set: when someone says '{trigger}', I will respond with '{response}'", ephemeral=True)

    @discord.app_commands.command(name="remove-auto-response", description="Remove an auto-response for a trigger.")
    async def remove_auto_response(self, interaction: discord.Interaction, trigger: str):
        from bot import is_user_blacklisted, is_server_blacklisted  # Import the helper functions
        if is_user_blacklisted(interaction.user.id):
            await interaction.response.send_message("You r blacklisted and cannot use any commands.", ephemeral=True)
            return       
        if is_server_blacklisted(interaction.user.id):
            await interaction.response.send_message('This server is blacklisted and you cannot use any commands', ephemeral=True)
            return
        if not interaction.user.guild_permissions.manage_messages:
            await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)
            return
        guild_id = interaction.guild_id
        if trigger.lower() in self.get_server_responses(guild_id):
            self.remove_server_response(guild_id, trigger)
            await interaction.response.send_message(f"Auto-response for '{trigger}' removed.", ephemeral=True)
        else:
            await interaction.response.send_message(f"No auto-response found for '{trigger}'.", ephemeral=True)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        
        guild_id = message.guild.id
        trigger = message.content.lower()
        server_responses = self.get_server_responses(guild_id)

        if trigger in server_responses:
            await message.channel.send(server_responses[trigger])

async def setup(bot):
    await bot.add_cog(AutoRespond(bot))
