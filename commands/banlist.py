import discord
from discord import app_commands
from discord.ext import commands

class BanListCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="banlist", description="Shows all banned users in the server")
    async def banlist(self, interaction: discord.Interaction):
        from bot import is_user_blacklisted, is_server_blacklisted  # Import the helper functions
        if is_user_blacklisted(interaction.user.id):
            await interaction.response.send_message("You r blacklisted and cannot use any commands.", ephemeral=True)
            return       
        if is_server_blacklisted(interaction.user.id):
            await interaction.response.send_message('This server is blacklisted and you cannot use any commands', ephemeral=True)
            return
        if not interaction.user.guild_permissions.ban_members:
            
            await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)
            return
        
        if not interaction.guild.me.guild_permissions.ban_members:
            await interaction.response.send_message("Sorry i dont have ban members permission to view the bans on this server")
            return

        bans = [entry async for entry in interaction.guild.bans()]
        if not bans:
            await interaction.response.send_message("There are no banned users in this server.", ephemeral=True)
            return

        ban_list = "\n".join([f"{ban.user} (ID: {ban.user.id})" for ban in bans])
        embed = discord.Embed(
            title="Banned Users",
            description=ban_list,
            color=discord.Color.red()
        )
        embed.set_footer(
            text=f"Requested by {interaction.user}",
            icon_url=interaction.user.display_avatar.url
        )
        embed.timestamp = discord.utils.utcnow()

        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(BanListCommand(bot))
