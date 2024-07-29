import discord
from discord.ext import commands
import psutil
from datetime import datetime, timedelta

class Statics(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.start_time = datetime.utcnow()  # Record the bot's start time

    @commands.Cog.listener()
    async def on_ready(self):
        print('Statics command loaded')

    def get_bot_uptime(self) -> str:
        now = datetime.utcnow()
        delta = now - self.start_time
        days, seconds = delta.days, delta.seconds
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60
        return f"{days}d, {hours}h, {minutes}m, {seconds}s"

    @discord.app_commands.command(name="statics", description="Shows the bot's statistics")
    async def statics(self, interaction: discord.Interaction):
        from bot import is_user_blacklisted, is_server_blacklisted  # Import the helper functions
        if is_user_blacklisted(interaction.user.id):
            await interaction.response.send_message("You r blacklisted and cannot use any commands.", ephemeral=True)
            return       
        if is_server_blacklisted(interaction.user.id):
            await interaction.response.send_message('This server is blacklisted and you cannot use any commands', ephemeral=True)
            return
        embed = discord.Embed(title="📊 Statistics", color=discord.Color.blue())
        
        # General Statistics
        total_guilds = len(self.bot.guilds)
        total_channels = sum([len(guild.channels) for guild in self.bot.guilds])
        total_members = sum([guild.member_count for guild in self.bot.guilds])

        embed.add_field(name="**General Statistics**", value=f"> - Servers : {total_guilds}\n> - Channels : {total_channels}\n> - Users : {total_members}", inline=False)
        
        # Uptime and Ping
        embed.add_field(name="Uptime and Ping", value=f"> - Uptime : {self.get_bot_uptime()}\n> - Ping : {round(self.bot.latency * 1000)} ms", inline=False)

        # Memory Usage
        memory = psutil.virtual_memory()
        memory_usage = f"{memory.used / 1024 ** 3:.2f} GB / {memory.total / 1024 ** 3:.2f} GB"
        memory_percent = f"{memory.percent}%"

        embed.add_field(name="**Memory**", value=f"> - Memory Usage : {memory_usage}\n> - Memory Percentage : {memory_percent}", inline=False)

        embed.set_thumbnail(url=self.bot.user.avatar.url)

        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Statics(bot))
