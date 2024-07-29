import discord
from discord.ext import commands

class Unban(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print('Unban command loaded')

    @discord.app_commands.command(name="unban", description="Unban a member from the server")
    async def unban(self, interaction: discord.Interaction, user: discord.User, reason: str = None):
        from bot import is_user_blacklisted, is_server_blacklisted  # Import the helper functions
        if is_user_blacklisted(interaction.user.id):
            await interaction.response.send_message("You r blacklisted and cannot use any commands.", ephemeral=True)
            return       
        if is_server_blacklisted(interaction.user.id):
            await interaction.response.send_message('This server is blacklisted and you cannot use any commands', ephemeral=True)
            return
        if not interaction.user.guild_permissions.ban_members:
            await interaction.response.send_message("Sorry, you don't have the right permissions to use this command.", ephemeral=True)
            return

        if not interaction.guild.me.guild_permissions.ban_members:
            await interaction.response.send_message("Sorry, I don't have the right permissions to do this.", ephemeral=True)
            return

        await interaction.guild.unban(user, reason=reason)
        await interaction.response.send_message(f"{user} has been unbanned from the server. Reason: {reason}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Unban(bot))
