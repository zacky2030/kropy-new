import discord
from discord.ext import commands

class RoleManagement(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.app_commands.command(name="give-role", description="Give a role to a user.")
    async def give_role(self, interaction: discord.Interaction, role: discord.Role, user: discord.Member):
        from bot import is_user_blacklisted, is_server_blacklisted  # Import the helper functions
        if is_user_blacklisted(interaction.user.id):
            await interaction.response.send_message("You r blacklisted and cannot use any commands.", ephemeral=True)
            return       
        if is_server_blacklisted(interaction.user.id):
            await interaction.response.send_message('This server is blacklisted and you cannot use any commands', ephemeral=True)
            return
        if not interaction.user.guild_permissions.manage_roles:
            await interaction.response.send_message("Sorry, you don't have the right permissions to use this command.", ephemeral=True)
            return

        if not interaction.guild.me.guild_permissions.manage_roles:
            await interaction.response.send_message("Sorry, I don't have the right permissions to do this.", ephemeral=True)
            return

        bot_member = interaction.guild.get_member(self.bot.user.id)
        if role.position >= bot_member.top_role.position:
            await interaction.response.send_message(f"The {role.mention} role is higher than my highest role, so I can't give it to {user.mention}.", ephemeral=True)
            return
        if role in user.roles:
            await interaction.response.send_message(f"{user.mention} already has the {role.mention} role.", ephemeral=True)
            return
        await user.add_roles(role)
        await interaction.response.send_message(f"Given the {role.mention} role to {user.mention}.", ephemeral=True)

    @discord.app_commands.command(name="remove-role", description="Remove a role from a user.")
    async def remove_role(self, interaction: discord.Interaction, user: discord.Member, role: discord.Role):
        from bot import is_user_blacklisted, is_server_blacklisted  # Import the helper functions
        if is_user_blacklisted(interaction.user.id):
            await interaction.response.send_message("You r blacklisted and cannot use any commands.", ephemeral=True)
            return       
        if is_server_blacklisted(interaction.user.id):
            await interaction.response.send_message('This server is blacklisted and you cannot use any commands', ephemeral=True)
            return
        if not interaction.user.guild_permissions.manage_roles:
            await interaction.response.send_message("Sorry, you don't have the right permissions to use this command.", ephemeral=True)
            return

        if not interaction.guild.me.guild_permissions.manage_roles:
            await interaction.response.send_message("Sorry, I don't have the right permissions to do this.", ephemeral=True)
            return

        bot_member = interaction.guild.get_member(self.bot.user.id)
        if role.position >= bot_member.top_role.position:
            await interaction.response.send_message(f"The {role.mention} role is higher than my highest role, so I can't remove it from {user.mention}.", ephemeral=True)
            return
        if role not in user.roles:
            await interaction.response.send_message(f"{user.mention} does not have the {role.mention} role.", ephemeral=True)
            return
        await user.remove_roles(role)
        await interaction.response.send_message(f"Removed the {role.mention} role from {user.mention}.", ephemeral=True)

    @discord.app_commands.command(name="roles", description="List all roles in the server.")
    async def roles(self, interaction: discord.Interaction):
        from bot import is_user_blacklisted, is_server_blacklisted  # Import the helper functions
        if is_user_blacklisted(interaction.user.id):
            await interaction.response.send_message("You r blacklisted and cannot use any commands.", ephemeral=True)
            return       
        if is_server_blacklisted(interaction.user.id):
            await interaction.response.send_message('This server is blacklisted and you cannot use any commands', ephemeral=True)
            return
        roles = interaction.guild.roles
        if not roles:
            await interaction.response.send_message("There are no roles in this server.", ephemeral=True)
            return

        sorted_roles = sorted(roles, key=lambda r: r.position, reverse=True)
        role_list = "\n".join([role.mention for role in sorted_roles if role != interaction.guild.default_role])

        embed = discord.Embed(title="Roles in this server", description=role_list, color=discord.Color.blue())
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @discord.app_commands.command(name="view-role-permissions", description="View the permissions of a role.")
    async def view_role_permissions(self, interaction: discord.Interaction, role: discord.Role):
        from bot import is_user_blacklisted, is_server_blacklisted  # Import the helper functions
        if is_user_blacklisted(interaction.user.id):
            await interaction.response.send_message("You r blacklisted and cannot use any commands.", ephemeral=True)
            return       
        if is_server_blacklisted(interaction.user.id):
            await interaction.response.send_message('This server is blacklisted and you cannot use any commands', ephemeral=True)
            return
        permissions = role.permissions
        perm_list = [perm.replace('_', ' ').title() for perm, value in permissions if value]
        perm_string = "\n".join(perm_list) if perm_list else "No permissions"
        
        embed = discord.Embed(title=f"Permissions for {role.name}", description=perm_string, color=discord.Color.blue())
        await interaction.response.send_message(embed=embed, ephemeral=True)


    @discord.app_commands.command(name="delete-role", description="Delete an existing role.")
    async def delete_role(self, interaction: discord.Interaction, role: discord.Role):
        from bot import is_user_blacklisted, is_server_blacklisted  # Import the helper functions
        if is_user_blacklisted(interaction.user.id):
            await interaction.response.send_message("You r blacklisted and cannot use any commands.", ephemeral=True)
            return       
        if is_server_blacklisted(interaction.user.id):
            await interaction.response.send_message('This server is blacklisted and you cannot use any commands', ephemeral=True)
            return
        if not interaction.user.guild_permissions.manage_roles:
            await interaction.response.send_message("Sorry, you don't have the right permissions to use this command.", ephemeral=True)
            return

        if not interaction.guild.me.guild_permissions.manage_roles:
            await interaction.response.send_message("Sorry, I don't have the right permissions to do this.", ephemeral=True)
            return

        bot_member = interaction.guild.get_member(self.bot.user.id)
        if role.position >= bot_member.top_role.position:
            await interaction.response.send_message(f"The {role.mention} role is higher than my highest role, so I can't delete it.", ephemeral=True)
            return

        await role.delete()
        await interaction.response.send_message(f"Deleted the {role.mention} role.", ephemeral=True)

    @discord.app_commands.command(name="rename-role", description="Rename an existing role.")
    async def rename_role(self, interaction: discord.Interaction, role: discord.Role, new_name: str):
        from bot import is_user_blacklisted, is_server_blacklisted  # Import the helper functions
        if is_user_blacklisted(interaction.user.id):
            await interaction.response.send_message("You r blacklisted and cannot use any commands.", ephemeral=True)
            return       
        if is_server_blacklisted(interaction.user.id):
            await interaction.response.send_message('This server is blacklisted and you cannot use any commands', ephemeral=True)
            return
        if not interaction.user.guild_permissions.manage_roles:
            await interaction.response.send_message("Sorry, you don't have the right permissions to use this command.", ephemeral=True)
            return

        if not interaction.guild.me.guild_permissions.manage_roles:
            await interaction.response.send_message("Sorry, I don't have the right permissions to do this.", ephemeral=True)
            return

        bot_member = interaction.guild.get_member(self.bot.user.id)
        if role.position >= bot_member.top_role.position:
            await interaction.response.send_message(f"The {role.mention} role is higher than my highest role, so I can't rename it.", ephemeral=True)
            return

        await role.edit(name=new_name)
        await interaction.response.send_message(f"Renamed the role to {role.mention}.", ephemeral=True)

    @discord.app_commands.command(name="role-info", description="Get information about a role.")
    async def role_info(self, interaction: discord.Interaction, role: discord.Role):
        from bot import is_user_blacklisted, is_server_blacklisted  # Import the helper functions
        if is_user_blacklisted(interaction.user.id):
            await interaction.response.send_message("You r blacklisted and cannot use any commands.", ephemeral=True)
            return       
        if is_server_blacklisted(interaction.user.id):
            await interaction.response.send_message('This server is blacklisted and you cannot use any commands', ephemeral=True)
            return
        embed = discord.Embed(title=f"Role Info: {role.name}", color=role.color)
        embed.add_field(name="ID", value=role.id, inline=False)
        embed.add_field(name="Color", value=str(role.color), inline=False)
        embed.add_field(name="Mentionable", value=str(role.mentionable), inline=False)
        embed.add_field(name="Position", value=str(role.position), inline=False)
        embed.add_field(name="Permissions", value=", ".join([perm[0].replace('_', ' ').title() for perm in role.permissions if perm[1]]), inline=False)
        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(RoleManagement(bot))
