import discord
from discord.ext import commands, tasks
import json
import os
import re
import requests

class LinkSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config_file = 'links.json'
        if not os.path.exists(self.config_file):
            with open(self.config_file, 'w') as f:
                json.dump({}, f)
        self.links = self.load_links()
        self.keep_alive.start()  # Start the keep-alive task

    def load_links(self):
        with open(self.config_file, 'r') as f:
            return json.load(f)

    def save_links(self):
        with open(self.config_file, 'w') as f:
            json.dump(self.links, f, indent=4)

    def is_valid_glitch_url(self, url):
        pattern = r'^https:\/\/[a-zA-Z0-9-]+\.glitch\.me$'
        return re.match(pattern, url) is not None

    @discord.app_commands.command(name="link-add", description="Add a Glitch project link to keep it online.")
    async def link_add(self, interaction: discord.Interaction, link: str):
        from bot import is_user_blacklisted, is_server_blacklisted  # Import the helper functions
        if is_user_blacklisted(interaction.user.id):
            await interaction.response.send_message("You r blacklisted and cannot use any commands.", ephemeral=True)
            return       
        if is_server_blacklisted(interaction.user.id):
            await interaction.response.send_message('This server is blacklisted and you cannot use any commands', ephemeral=True)
            return
        if not self.is_valid_glitch_url(link):
            await interaction.response.send_message("Invalid Glitch URL. Make sure it ends with 'yourprojectname.glitch.me'.", ephemeral=True)
            return
        
        user_id = str(interaction.user.id)
        if user_id not in self.links:
            self.links[user_id] = []

        if link in self.links[user_id]:
            await interaction.response.send_message("You have already added this link.", ephemeral=True)
            return

        self.links[user_id].append(link)
        self.save_links()
        await interaction.response.send_message(f"Link added: {link}", ephemeral=True)

    @discord.app_commands.command(name="link-delete", description="Delete a Glitch project link.")
    async def link_delete(self, interaction: discord.Interaction, link: str):
        from bot import is_user_blacklisted, is_server_blacklisted  # Import the helper functions
        if is_user_blacklisted(interaction.user.id):
            await interaction.response.send_message("You r blacklisted and cannot use any commands.", ephemeral=True)
            return       
        if is_server_blacklisted(interaction.user.id):
            await interaction.response.send_message('This server is blacklisted and you cannot use any commands', ephemeral=True)
            return
        user_id = str(interaction.user.id)
        if user_id not in self.links or link not in self.links[user_id]:
            await interaction.response.send_message("Link not found in your list.", ephemeral=True)
            return

        self.links[user_id].remove(link)
        self.save_links()
        await interaction.response.send_message(f"Link deleted: {link}", ephemeral=True)

    @discord.app_commands.command(name="mylinks", description="Show your Glitch project links.")
    async def mylinks(self, interaction: discord.Interaction):
        from bot import is_user_blacklisted, is_server_blacklisted  # Import the helper functions
        if is_user_blacklisted(interaction.user.id):
            await interaction.response.send_message("You r blacklisted and cannot use any commands.", ephemeral=True)
            return       
        if is_server_blacklisted(interaction.user.id):
            await interaction.response.send_message('This server is blacklisted and you cannot use any commands', ephemeral=True)
            return
        user_id = str(interaction.user.id)
        if user_id not in self.links or not self.links[user_id]:
            await interaction.response.send_message("You have no links added.", ephemeral=True)
            return

        links = "\n".join(self.links[user_id])
        await interaction.response.send_message(f"Your links:\n{links}", ephemeral=True)

    @discord.app_commands.command(name="total-links", description="Show the total number of links added.")
    async def total_links(self, interaction: discord.Interaction):
        from bot import is_user_blacklisted, is_server_blacklisted  # Import the helper functions
        if is_user_blacklisted(interaction.user.id):
            await interaction.response.send_message("You r blacklisted and cannot use any commands.", ephemeral=True)
            return       
        if is_server_blacklisted(interaction.user.id):
            await interaction.response.send_message('This server is blacklisted and you cannot use any commands', ephemeral=True)
            return
        user_id = str(interaction.user.id)
        user_links_count = len(self.links.get(user_id, []))
        total_links_count = sum(len(links) for links in self.links.values())
        await interaction.response.send_message(f"You have added {user_links_count} link(s).\nTotal links in the bot: {total_links_count}", ephemeral=True)

    @tasks.loop(minutes=3)  # Adjust the interval to 3 minute
    async def keep_alive(self):
        for user_links in self.links.values():
            for link in user_links:
                try:
                    requests.get(link)
                except requests.RequestException:
                    pass

    @keep_alive.before_loop
    async def before_keep_alive(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(LinkSystem(bot))

