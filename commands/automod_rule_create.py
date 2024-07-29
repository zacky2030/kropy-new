import discord
from discord.ext import commands
import json

class AutomodRuleCreate(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.app_commands.command(name="automod-rule-create", description="Create an auto moderation rule.")
    @discord.app_commands.describe(name="The name of the rule", trigger="The trigger keyword or phrase", action="The action to take (mute, kick, ban)")
    async def automod_rule_create(self, interaction: discord.Interaction, name: str, trigger: str, action: str):
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

        # Define the payload for the auto moderation rule
        payload = {
            "name": name,
            "event_type": 1,  # MESSAGE_SEND event
            "trigger_type": 1,  # KEYWORD trigger type
            "trigger_metadata": {
                "keyword_filter": [trigger]
            },
            "actions": [
                {
                    "type": 1,  # Block message
                }
            ]
        }

        # Retrieve the current channel ID
        channel_id = interaction.channel_id

        if action == 'mute':
            payload['actions'].append({
                "type": 2,  # Timeout action
                "metadata": {
                    "duration_seconds": 600,  # Mute for 10 minutes
                    "channel_id": channel_id
                }
            })
        elif action == 'kick':
            payload['actions'].append({
                "type": 3,  # Kick action
                "metadata": {
                    "channel_id": channel_id
                }
            })
        elif action == 'ban':
            payload['actions'].append({
                "type": 4,  # Ban action
                "metadata": {
                    "channel_id": channel_id
                }
            })

        # Send the request to the Discord API with error handling
        try:
            response = await self.bot.http.request(
                discord.http.Route('POST', f'/guilds/{interaction.guild_id}/auto-moderation/rules'),
                json=payload
            )
            if 'id' in response:
                await interaction.response.send_message(f"Auto moderation rule '{name}' created with trigger '{trigger}' and action '{action}'.",ephemeral=True)
            else:
                await interaction.response.send_message(f"Failed to create auto moderation rule: {response}.", ephemeral=True)
        except discord.errors.HTTPException as e:
            await interaction.response.send_message(f"An error occurred while creating the auto moderation rule: {e.status}. {e.text}", ephemeral=True)
        except discord.errors.DiscordServerError as e:
            await interaction.response.send_message(f"Discord server error: {e.status}. The server might be temporarily unavailable. Please try again later.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"An unexpected error occurred: {str(e)}.")

async def setup(bot):
    await bot.add_cog(AutomodRuleCreate(bot))
