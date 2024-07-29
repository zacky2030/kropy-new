import discord
from discord.ext import commands

class Hello(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print('Hello command loaded')

    @discord.app_commands.command(name="hello", description="Say hello to the bot")
    async def hello(self, interaction: discord.Interaction):
        from bot import is_user_blacklisted, is_server_blacklisted  # Import the helper functions
        if is_user_blacklisted(interaction.user.id):
            await interaction.response.send_message("You r blacklisted and cannot use any commands.", ephemeral=True)
            return       
        if is_server_blacklisted(interaction.user.id):
            await interaction.response.send_message('This server is blacklisted and you cannot use any commands', ephemeral=True)
            return
        await interaction.response.send_message("Hello! How can I help you today?")

async def setup(bot):
    await bot.add_cog(Hello(bot))
