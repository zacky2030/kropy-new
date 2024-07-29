import discord
from discord.ext import commands

class HelpCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.app_commands.command(name="help", description="Show help information.")
    async def help(self, interaction: discord.Interaction):
        from bot import is_user_blacklisted, is_server_blacklisted  # Import the helper functions
        if is_user_blacklisted(interaction.user.id):
            await interaction.response.send_message("You r blacklisted and cannot use any commands.", ephemeral=True)
            return       
        if is_server_blacklisted(interaction.user.id):
            await interaction.response.send_message('This server is blacklisted and you cannot use any commands', ephemeral=True)
            return
        # Define categories and their respective commands
        command_categories = {
            "Auto Moderation": [
                "automod-rule-create", "automod-rule-delete", "automod-rule-disable", "automod-rule-enable"
            ],
            "User Management": [
                "ban", "banlist", "banlog", "kick", "kick-log", "nuke", "timeout", "unban", "untimeout", "warnsystem", 
                "vdeafen", "vundeafen", "vmute", "vunmute", "vkick"
            ],
            "Utility": [
                "avatar", "delete", "dm", "hello", "invite", "ping", "serverinfo", "userinfo"
            ],
            "Logs": [
                "set-join-logs","disable-join-log", "set-leave-log", "disable-leave-log" "set-message-logs", "disable-message-log" 
                "role-logs", "set-user-activity-logs", "disable-user-activity-log","voicelog-set", "voicelog-disable"
            ],
            "Roles": [
                "role-create", "role-remove", "roles", "role-info", "role-set-permissions", "view-role-permissions", "rename-role", 
                "delete-role", "give-role"
            ],
            "Levels": [
                "set-level-system", "disable-level-system"
            ],
            "Uptime": [
                "link-add", "mylinks", "link-delete", "total-links",
            ],
            "Statics": [
                "statics"
            ],
            "Ticket System": [
                "create-ticket-system", "delete-ticket-system", "disable-ticket-system", "enable-ticket-system"
            ],
            "Auto Response": [
                "set-auto-respond", "disable-auto-respond"
            ]
        }

        category_options = [
            discord.SelectOption(label=category, description=f"{category} commands", value=category)
            for category in command_categories.keys()
        ]

        category_select = discord.ui.Select(
            placeholder="Choose a category",
            min_values=1,
            max_values=1,
            options=category_options
        )

        async def category_select_callback(interaction: discord.Interaction):
            selected_category = category_select.values[0]
            commands_list = command_categories[selected_category]
            commands_str = "\n".join(f"`{cmd}`" for cmd in commands_list)

            embed = discord.Embed(title=f"{selected_category} Commands", description=commands_str, color=discord.Color.blue())
            await interaction.response.send_message(embed=embed, ephemeral=True)

        category_select.callback = category_select_callback

        view = discord.ui.View()
        view.add_item(category_select)
        await interaction.response.send_message("Select a category to get help:", view=view, ephemeral=True)

async def setup(bot):
    await bot.add_cog(HelpCommand(bot))
