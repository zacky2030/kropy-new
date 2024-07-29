import discord
from discord.ext import commands
from discord.utils import utcnow
from datetime import timedelta

class Timeout(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print('Timeout command loaded')

    def parse_duration(self, duration_str: str) -> timedelta:
        unit = duration_str[-1]
        amount = int(duration_str[:-1])

        if unit == 's':
            return timedelta(seconds=amount)
        elif unit == 'm':
            return timedelta(minutes=amount)
        elif unit == 'h':
            return timedelta(hours=amount)
        elif unit == 'd':
            return timedelta(days=amount)
        elif unit == 'w':
            return timedelta(weeks=amount)
        else:
            raise ValueError("Invalid duration unit. Use s, m, h, d, or w.")

    @discord.app_commands.command(name="timeout", description="Timeout a member")
    async def timeout(self, interaction: discord.Interaction, member: discord.Member, duration: str, reason: str = None):
        from bot import is_user_blacklisted, is_server_blacklisted  # Import the helper functions
        if is_user_blacklisted(interaction.user.id):
            await interaction.response.send_message("You r blacklisted and cannot use any commands.", ephemeral=True)
            return       
        if is_server_blacklisted(interaction.user.id):
            await interaction.response.send_message('This server is blacklisted and you cannot use any commands', ephemeral=True)
            return
        if member == interaction.user :
            await interaction.response.send_message("You can't timeout yourself, Silly 😋", ephemeral=True)
            
        if not interaction.user.guild_permissions.moderate_members:
            await interaction.response.send_message("Sorry, you don't have the right permissions to use this command.", ephemeral=True)
            return

        if not interaction.guild.me.guild_permissions.moderate_members:
            await interaction.response.send_message("Sorry, I don't have the right permissions to do this.", ephemeral=True)
            return
        
        if member.top_role >= interaction.guild.me.top_role:
            await interaction.response.send_message("I can't timeout the user you provided, they have a higher permission than me!", ephemeral=True)
            return

        try:
            timeout_duration = self.parse_duration(duration)
        except ValueError as e:
            await interaction.response.send_message(str(e), ephemeral=True)
            return

        timeout_until = utcnow() + timeout_duration

        print(f"Timeout until: {timeout_until}")  # Debug print

        try:
            await member.edit(timed_out_until=timeout_until, reason=reason)
            await interaction.response.send_message(f"{member} has been timed out for {duration}. Reason: {reason}", ephemeral=True)
        except Exception as e:
            print(f"Error: {e}")  # Debug print
            await interaction.response.send_message(f"Failed to timeout {member}: {str(e)}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Timeout(bot))
