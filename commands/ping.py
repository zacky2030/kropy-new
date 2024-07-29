import discord
from discord.ext import commands

class Ping(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print('Ping command loaded')

    @discord.app_commands.command(name="ping", description="Shows the bot's latency")
    async def ping(self, interaction: discord.Interaction):
        from bot import is_user_blacklisted, is_server_blacklisted  # Import the helper functions
        if is_user_blacklisted(interaction.user.id):
            await interaction.response.send_message("You r blacklisted and cannot use any commands.", ephemeral=True)
            return       
        if is_server_blacklisted(interaction.user.id):
            await interaction.response.send_message('This server is blacklisted and you cannot use any commands', ephemeral=True)
            return
        latency = self.bot.latency * 1000  # Convert to milliseconds
        micro_latency = latency * 1000     # Microseconds for demonstration
        ws_latency = latency               # WebSocket latency

        embed = discord.Embed(
            title="Pong! :ping_pong:",
            description=(
                f":hourglass_flowing_sand: **Ping:** {latency:.2f} ms\n"
                f":sparkling_heart: **WebSocket:** {ws_latency:.2f} ms"
            ),
            color=discord.Color.darker_grey()
        )

        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Ping(bot))
