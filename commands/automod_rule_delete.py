import discord
from discord.ext import commands

class AutomodRuleDelete(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.app_commands.command(name="automod-rule-delete", description="Delete an auto moderation rule.")
    @discord.app_commands.describe(rule_id="The ID of the rule to delete")
    async def automod_rule_delete(self, interaction: discord.Interaction, rule_id: str):
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

        # Send the request to the Discord API
        try:
            response = await self.bot.http.request(
                discord.http.Route('DELETE', f'/guilds/{interaction.guild_id}/auto-moderation/rules/{rule_id}')
            )

            # Check if the response is empty which indicates success
            if not response:
                await interaction.response.send_message(f"Auto moderation rule with ID '{rule_id}' has been deleted.", ephemeral=True)
            else:
                await interaction.response.send_message(f"Failed to delete auto moderation rule: {response}.", ephemeral=True)
        except discord.errors.HTTPException as e:
            await interaction.response.send_message(f"An error occurred while deleting the auto moderation rule: {e.status}. {e.text}", ephemeral=True)
        except discord.errors.DiscordServerError as e:
            await interaction.response.send_message(f"Discord server error: {e.status}. The server might be temporarily unavailable. Please try again later.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"An unexpected error occurred: {str(e)}.")

async def setup(bot):
    await bot.add_cog(AutomodRuleDelete(bot))
