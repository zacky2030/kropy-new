import discord
from discord.ext import commands

class ServerInfo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.app_commands.command(name="serverinfo", description="Displays information about the server.")
    async def serverinfo(self, interaction: discord.Interaction):
        from bot import is_user_blacklisted, is_server_blacklisted  # Import the helper functions
        if is_user_blacklisted(interaction.user.id):
            await interaction.response.send_message("You r blacklisted and cannot use any commands.", ephemeral=True)
            return       
        if is_server_blacklisted(interaction.user.id):
            await interaction.response.send_message('This server is blacklisted and you cannot use any commands', ephemeral=True)
            return
        guild = interaction.guild
        embed = discord.Embed(title=f"Server Info - {guild.name}", color=discord.Color.blue())
        embed.set_thumbnail(url=guild.icon.url if guild.icon else None)

        embed.add_field(name="📛 Server Name", value=guild.name, inline=True)
        embed.add_field(name="🆔 Server ID", value=guild.id, inline=True)
        embed.add_field(name="👑 Owner", value=guild.owner.mention, inline=True)
        embed.add_field(name="👥 Member Count", value=guild.member_count, inline=True)
        embed.add_field(name="📅 Created At", value=guild.created_at.strftime("%Y-%m-%d %H:%M:%S"), inline=True)

        # List the voice regions in use on the server
        voice_regions = []
        for channel in guild.voice_channels:
            voice_regions.append(f"{channel.name}: {channel.rtc_region}")
        
        if voice_regions:
            embed.add_field(name="🌍 Voice Regions", value="\n".join(voice_regions), inline=False)
        else:
            embed.add_field(name="🌍 Voice Regions", value="No voice channels available", inline=False)

        embed.set_footer(text=f"Requested by {interaction.user}", icon_url=interaction.user.avatar.url if interaction.user.avatar else None)
        
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(ServerInfo(bot))
