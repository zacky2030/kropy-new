import discord
from discord.ext import commands

class Kick(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print('Kick command loaded')

    @discord.app_commands.command(name="kick", description="Kick a member from the server")
    async def kick(self, interaction: discord.Interaction, member: discord.Member, reason: str = None):
        from bot import is_user_blacklisted, is_server_blacklisted  # Import the helper functions
        if is_user_blacklisted(interaction.user.id):
            await interaction.response.send_message("You r blacklisted and cannot use any commands.", ephemeral=True)
            return       
        if is_server_blacklisted(interaction.user.id):
            await interaction.response.send_message('This server is blacklisted and you cannot use any commands', ephemeral=True)
            return
        if member == interaction.user :
            await interaction.response.send_message("You can't kick yourself, Silly 😋", ephemeral=True)
        
        if not interaction.user.guild_permissions.kick_members:
            await interaction.response.send_message("Sorry, you don't have the right permissions to use this command.", ephemeral=True)
            return

        if not interaction.guild.me.guild_permissions.kick_members:
            await interaction.response.send_message("Sorry, I don't have the right permissions to do this.", ephemeral=True)
            return
        
        if member.top_role >= interaction.guild.me.top_role:
            await interaction.response.send_message("I can't kick the user you provided, they have a higher permission than me!", ephemeral=True)
            return

        await member.kick(reason=reason)
        await interaction.response.send_message(f"{member} has been kicked from the server. Reason: {reason}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Kick(bot))
