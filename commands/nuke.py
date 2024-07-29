import discord
from discord.ext import commands

class Nuke(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print('Nuke command loaded')

    @discord.app_commands.command(name="nuke", description="Delete's every single message in the channel")
    async def nuke(self, interaction: discord.Interaction):
        from bot import is_user_blacklisted, is_server_blacklisted  # Import the helper functions
        if is_user_blacklisted(interaction.user.id):
            await interaction.response.send_message("You r blacklisted and cannot use any commands.", ephemeral=True)
            return       
        if is_server_blacklisted(interaction.user.id):
            await interaction.response.send_message('This server is blacklisted and you cannot use any commands', ephemeral=True)
            return
        if not interaction.user.guild_permissions.manage_messages:
            await interaction.response.send_message("Sorry, you don't have the right permissions to use this command.")
            return

        if not interaction.channel.permissions_for(interaction.guild.me).manage_messages:
            await interaction.response.send_message("Sorry, I don't have the right permissions to do this.")
            return

        await interaction.response.send_message("Nuking the channel...", ephemeral=True)
        
        channel = interaction.channel
        await channel.purge(limit=None)
        
        await channel.send("This channel has been nuked!", ephemerel=True)

async def setup(bot):
    await bot.add_cog(Nuke(bot))
