import discord
from discord.ext import commands

class Untimeout(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print('Untimeout command loaded')

    @discord.app_commands.command(name="untimeout", description="Remove timeout from a member")
    async def untimeout(self, interaction: discord.Interaction, member: discord.Member, reason: str = None):
        from bot import is_user_blacklisted, is_server_blacklisted  # Import the helper functions
        if is_user_blacklisted(interaction.user.id):
            await interaction.response.send_message("You r blacklisted and cannot use any commands.", ephemeral=True)
            return       
        if is_server_blacklisted(interaction.user.id):
            await interaction.response.send_message('This server is blacklisted and you cannot use any commands', ephemeral=True)
            return
        if not interaction.user.guild_permissions.moderate_members:
            await interaction.response.send_message("Sorry, you don't have the right permissions to use this command.", ephemeral=True)
            return

        if not interaction.guild.me.guild_permissions.moderate_members:
            await interaction.response.send_message("Sorry, I don't have the right permissions to do this.", ephemeral=True)
            return

        await member.timeout(None, reason=reason)
        await interaction.response.send_message(f"Timeout for {member} has been removed. Reason: {reason}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Untimeout(bot))
