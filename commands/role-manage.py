import discord
from discord import app_commands
from discord.ext import commands

class RoleCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="role-create", description="Creates a role with specified name and color")
    @app_commands.describe(
        name="The name of the role",
        color="The color of the role in hexadecimal"
    )
    async def role_create(self, interaction: discord.Interaction, name: str, color: str = "0x000000"):
        from bot import is_user_blacklisted, is_server_blacklisted  # Import the helper functions
        if is_user_blacklisted(interaction.user.id):
            await interaction.response.send_message("You r blacklisted and cannot use any commands.", ephemeral=True)
            return       
        if is_server_blacklisted(interaction.user.id):
            await interaction.response.send_message('This server is blacklisted and you cannot use any commands', ephemeral=True)
            return
        if not interaction.user.guild_permissions.manage_roles:
            await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)
            return

        color = int(color.replace("#", ""), 16)
        role = await interaction.guild.create_role(name=name, color=discord.Color(color))
        await interaction.response.send_message(f"Role `{role.name}` created. You can set its permissions using `/role-set-permissions` command.", ephemeral=True)

    @app_commands.command(name="role-set-permissions", description="Sets permissions for a role")
    @app_commands.describe(
        role="The role to set permissions for",
        permissions="The permissions to set (comma-separated list of permissions)"
    )
    async def role_set_permissions(self, interaction: discord.Interaction, role: discord.Role, permissions: str):
        from bot import is_user_blacklisted, is_server_blacklisted  # Import the helper functions
        if is_user_blacklisted(interaction.user.id):
            await interaction.response.send_message("You r blacklisted and cannot use any commands.", ephemeral=True)
            return       
        if is_server_blacklisted(interaction.user.id):
            await interaction.response.send_message('This server is blacklisted and you cannot use any commands', ephemeral=True)
            return
        if not interaction.user.guild_permissions.manage_roles:
            await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)
            return

        perm_list = permissions.split(',')
        perm_dict = {perm.strip(): True for perm in perm_list}
        role_perms = discord.Permissions(**perm_dict)
        await role.edit(permissions=role_perms)
        await interaction.response.send_message(f"Permissions for role `{role.name}` have been updated.", ephemeral=True)

    @app_commands.command(name="role-give", description="Gives a role to a member")
    @app_commands.describe(member="The member to give the role to", role="The role to give to the member")
    async def role_give(self, interaction: discord.Interaction, member: discord.Member, role: discord.Role):
        from bot import is_user_blacklisted, is_server_blacklisted  # Import the helper functions
        if is_user_blacklisted(interaction.user.id):
            await interaction.response.send_message("You r blacklisted and cannot use any commands.", ephemeral=True)
            return       
        if is_server_blacklisted(interaction.user.id):
            await interaction.response.send_message('This server is blacklisted and you cannot use any commands', ephemeral=True)
            return
        if not interaction.user.guild_permissions.manage_roles:
            await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)
            return
        if not interaction.guild.me.guild_permissions.manage_roles:
            await interaction.response.send_message("I don't have permission to use this command.", ephemeral=True)
            return

        bot_member = interaction.guild.get_member(self.bot.user.id)
        if role >= bot_member.top_role:
            await interaction.response.send_message(f"Sorry, I can't give {member.mention} that role because I don't have enough permissions for that.", ephemeral=True)
            return

        if role in member.roles:
            await interaction.response.send_message(f"{member.mention} already has the {role.mention} role.", ephemeral=True)
        else:
            await member.add_roles(role)
            await interaction.response.send_message(f"Successfully gave {role.mention} role to {member.mention}.", ephemeral=True)

    @app_commands.command(name="role-remove", description="Removes a role from a member")
    @app_commands.describe(member="The member to remove the role from", role="The role to remove from the member")
    async def role_remove(self, interaction: discord.Interaction, member: discord.Member, role: discord.Role):
        from bot import is_user_blacklisted, is_server_blacklisted  # Import the helper functions
        if is_user_blacklisted(interaction.user.id):
            await interaction.response.send_message("You r blacklisted and cannot use any commands.", ephemeral=True)
            return       
        if is_server_blacklisted(interaction.user.id):
            await interaction.response.send_message('This server is blacklisted and you cannot use any commands', ephemeral=True)
            return
        if not interaction.user.guild_permissions.manage_roles:
            await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)
            return
        
        if not interaction.guild.me.guild_permissions.manage_roles:
            await interaction.response.send_message("I don't have permission to use this command.", ephemeral=True)
            return

        bot_member = interaction.guild.get_member(self.bot.user.id)
        if role >= bot_member.top_role:
            await interaction.response.send_message(f"Sorry, I can't remove that role from {member.mention} because I don't have enough permissions for that.", ephemeral=True)
            return

        if role not in member.roles:
            await interaction.response.send_message(f"{member.mention} does not have the {role.mention} role.", ephemeral=True)
        else:
            await member.remove_roles(role)
            await interaction.response.send_message(f"Successfully removed {role.mention} role from {member.mention}.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(RoleCommand(bot))
