import discord
from discord.ext import commands
import aiohttp

class AutomodRuleEnable(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.app_commands.command(name="automod-rule-enable", description="Enable an auto moderation rule.")
    @discord.app_commands.describe(rule_name="The name of the rule to enable")
    async def automod_rule_enable(self, interaction: discord.Interaction, rule_name: str):
        from bot import is_user_blacklisted, is_server_blacklisted  # Import the helper functions
        if is_user_blacklisted(interaction.user.id):
            await interaction.response.send_message("You r blacklisted and cannot use any commands.", ephemeral=True)
            return       
        if is_server_blacklisted(interaction.user.id):
            await interaction.response.send_message('This server is blacklisted and you cannot use any commands', ephemeral=True)
            return
        # Check for permissions
        if not interaction.user.guild_permissions.manage_guild:
            await interaction.response.send_message("Sorry, you don't have the right permissions to use this command.", ephemeral=True)
            return

        if not interaction.guild.me.guild_permissions.manage_guild:
            await interaction.response.send_message("Sorry, I don't have the right permissions to do this.", ephemeral=True)
            return

        async with aiohttp.ClientSession() as session:
            # Fetch all auto moderation rules
            async with session.get(f'https://discord.com/api/v9/guilds/{interaction.guild_id}/auto-moderation/rules',
                                   headers={'Authorization': f'Bot {self.bot.http.token}'}) as resp:
                if resp.status != 200:
                    await interaction.response.send_message(f"Failed to fetch auto moderation rules: {resp.status}.", ephemeral=True)
                    return

                rules = await resp.json()

            # Find the rule with the given name
            rule = next((r for r in rules if r['name'].lower() == rule_name.lower()), None)
            if not rule:
                await interaction.response.send_message(f"No rule found with the name '{rule_name}'.", ephemeral=True)
                return

            # Enable the rule
            rule_id = rule['id']
            payload = {
                "enabled": True
            }

            async with session.patch(f'https://discord.com/api/v9/guilds/{interaction.guild_id}/auto-moderation/rules/{rule_id}',
                                     json=payload,
                                     headers={'Authorization': f'Bot {self.bot.http.token}'}) as resp:
                if resp.status == 200:
                    await interaction.response.send_message(f"Auto moderation rule '{rule_name}' has been enabled.", ephemeral=True)
                else:
                    await interaction.response.send_message(f"Failed to enable auto moderation rule '{rule_name}': {resp.status}.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(AutomodRuleEnable(bot))
