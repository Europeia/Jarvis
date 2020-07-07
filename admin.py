import discord
from discord.ext import commands

from config.config_manager import BaseConfigManager


class AdministrationCommands(commands.Cog):
    def __init__(self, bot, configMgr: BaseConfigManager):
        self.bot = bot
        self.configManager = configMgr

    @commands.command()
    @commands.guild_only()
    async def addRole(self, ctx, role: discord.Role, member: discord.Member):
        """Adds a Role to a user: !addRole <Role> <User>"""
        if not (
            self.configManager.isCommander(ctx.guild, role, ctx.author) or
            (
                ctx.author.guild_permissions.manage_roles and
                ctx.author.top_role.position >= role.position
            )
        ):
            await ctx.send("You don't have permission to add users to roles!")
            return
        await member.add_roles(role, reason='Added by ' + ctx.author.name)
        await ctx.send('Added ' + member.name + ' to @' + role.name)

    @addRole.error
    async def addRole_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            if 'Role ' in error.args[0]:
                await ctx.send('Invalid Role! Usage: !addRole <role> <user>')
            if 'Member ' in error.args[0]:
                await ctx.send('Invalid Member! Usage: !addRole <role> <user>')
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('ERROR! Usage: !addRole <role> <user>')
        else:
            await ctx.send(error.args[0])

    @commands.command()
    @commands.guild_only()
    async def joinRole(self, ctx, role: discord.Role):
        """Joins a Joinable Role: !joinRole <role>"""
        if not self.configManager.isJoinableRole(ctx.guild, role):
            await ctx.send('@' + role.name + ' isn\'t joinable.')
            return
        await ctx.author.add_roles(role, reason='Adding to Joinable Role by ' + ctx.author.name)
        await ctx.send('Joined @' + role.name)

    @joinRole.error
    async def joinRole_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            if 'Role ' in error.args[0]:
                await ctx.send('Invalid Role! Usage: !joinRole <role>')
            elif isinstance(error, commands.MissingRequiredArgument):
                await ctx.send('ERROR! Usage: !joinRole <role>')
        else:
            await ctx.send(error.args[0])

    @commands.command()
    @commands.guild_only()
    async def remRole(self, ctx, role: discord.Role, member: discord.Member):
        """Removes a Role from a user: !remRole <Role> <User>"""
        if not (
            self.configManager.isCommander(ctx.guild, role, ctx.author) or
            (
                ctx.author.guild_permissions.manage_roles and
                ctx.author.top_role.position >= role.position
            )
        ):
            await ctx.send("You don't have permission to add users to roles!")
            return
        await member.remove_roles(role, reason='Removed by ' + ctx.author.name)
        await ctx.send('Removed ' + member.name + ' from @' + role.name)

    @remRole.error
    async def remRole_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            if 'Role ' in error.args[0]:
                await ctx.send('Invalid Role! Usage: !remRole <role> <user>')
            elif 'Member ' in error.args[0]:
                await ctx.send('Invalid Member! Usage: !remRole <role> <user>')
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('ERROR! Usage: !remRole <role> <user>')
        else:
            await ctx.send(error.args[0])

    @commands.command()
    @commands.guild_only()
    async def leaveRole(self, ctx, role: discord.Role):
        """Leaves a Joinable Role: !leaveRole <role>"""
        if not self.configManager.isJoinableRole(ctx.guild, role):
            await ctx.send('@' + role.name + ' isn\'t joinable.')
            return
        await ctx.author.remove_roles(role, reason='Leaving a Joinable Role by ' + ctx.author.name)
        await ctx.send('Left @' + role.name)

    @leaveRole.error
    async def leaveRole_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            if 'Role ' in error.args[0]:
                await ctx.send('Invalid Role! Usage: !leaveRole <role>')
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('ERROR! Usage: !leaveRole <role>')
        else:
            await ctx.send(error.args[0])

    @commands.command()
    @commands.guild_only()
    async def listJoinableRoles(self, ctx):
        """Lists all Joinable roles: !listJoinableRoles"""
        joinableRoles = self.configManager.getJoinableRoles(ctx.guild)
        output = 'Joinable Roles:\n'
        if len(joinableRoles) == 0:
            output += 'None'
        else:
            for roleId in joinableRoles:
                role = None
                for guildRole in ctx.guild.roles:
                    if guildRole.id == roleId:
                        role = guildRole
                        break
                if role is not None:
                    output += role.name + '\n'
        await ctx.send(output)

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def addRoleMgr(self, ctx, role: discord.Role, member: discord.Member):
        """Adds a RoleManager to a Role: !addRoleMgr <Role> <User>"""
        self.configManager.addCommander(ctx.guild, role, member)
        self.configManager.writeConfig()
        await ctx.send(member.name + ' can now add users to ' + role.name)

    @addRoleMgr.error
    async def addRoleMgr_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            if 'Role ' in error.args[0]:
                await ctx.send('Invalid Role! Usage: !addRoleMgr <role> <user>')
            elif 'Member ' in error.args[0]:
                await ctx.send('Invalid Member! Usage: !addRoleMgr <role> <user>')
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('ERROR! Usage: !addRoleMgr <role> <user>')
        else:
            await ctx.send(error.args[0])

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def remRoleMgr(self, ctx, role: discord.Role, member: discord.Member):
        """Removes a RoleManager from a Role: !remRoleMgr <Role> <User>"""
        self.configManager.remCommander(ctx.guild, role, member)
        self.configManager.writeConfig()
        await ctx.send(member.name + ' can no longer add users to ' + role.name)

    @remRoleMgr.error
    async def remRoleMgr_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            if 'Role ' in error.args[0]:
                await ctx.send('Invalid Role! Usage: !remRoleMgr <role> <user>')
            elif 'Member ' in error.args[0]:
                await ctx.send('Invalid Member! Usage: !remRoleMgr <role> <user>')
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('ERROR! Usage: !remRoleMgr <role> <user>')
        else:
            await ctx.send(error.args[0])

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def listRoleData(self, ctx, role: discord.Role):
        """Lists Role Data for a Role: !listRoleData <role>"""
        output = 'Config Data for Role - ' + \
            role.name + ' : ' + str(role.id) + '\n'
        output += 'Joinable Group: ' + \
            str(self.configManager.isJoinableRole(ctx.guild, role)) + '\n'

        commanders = self.configManager.listCommanders(ctx.guild, role)
        if len(commanders) < 1:
            commanders = 'None'
        output += 'Managers for @' + role.name + ':\n' + commanders

        await ctx.send(output)

    @listRoleData.error
    async def listRoleData_error(self, ctx, error):
        if isinstance(error,  commands.BadArgument):
            await ctx.send('Invalid Role! Usage: !listRoleData <role>')
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('ERROR! Usage: !listRoleData <role>')
        else:
            await ctx.send(error.args[0])

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def toggleJoinableRole(self, ctx, role: discord.Role):
        """Makes a role Joinable by any user"""
        joinable = self.configManager.isJoinableRole(ctx.guild, role)
        self.configManager.setJoinableRole(ctx.guild, role, not joinable)
        self.configManager.writeConfig()
        await ctx.send('Joinable Group for @' + role.name + ' set to ' + str(not joinable))

    @toggleJoinableRole.error
    async def toggleJoinableRole_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send('Invalid Role! Usage: !toggleJoinableRole <role>')
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('ERROR! Usage: !toggleJoinableRole <role>')
        else:
            await ctx.send(error.args[0])

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def setGreetingMessage(self, ctx, *, greetingMessage: str):
        """Sets the Greeting Message sent to all new members of the Server (set to 'none' to disable)"""
        self.configManager.setGreetingMessage(ctx.guild,  greetingMessage)
        self.configManager.writeConfig()
        await ctx.send('New Greeting Message Set!')

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def getGreetingMessage(self,  ctx):
        """Shows the Greeting Message sent to all new members of the server (if 'none' no message will be sent)"""
        await ctx.send(self.configManager.getGreetingMessage(ctx.guild))

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def getGateData(self, ctx):
        """Shows Gate Data for the server"""
        guild = ctx.guild
        gateData = self.configManager.getGateData(guild)
        gateRole = guild.get_role(gateData.key_role_id)
        gateRoleName = gateRole.name if gateRole is not None else 'None'

        output = 'Data for ' + guild.name + ' (' + str(guild.id) + ')\n'
        output += 'Gate Enabled: ' + str(gateData.gate_enabled) + '\n'
        output += 'Gate Role:' + gateRoleName + '\n'
        output += 'Gate Allows Rejoin: ' + str(gateData.allow_rejoin) + '\n'

        await ctx.send(output)

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def setGateEnabled(self, ctx: commands.Context, gated: bool):
        """Sets Gate Enabled for the server"""
        guild = ctx.guild
        gateData = self.configManager.getGateData(guild)
        gateRole = guild.get_role(gateData.key_role_id)

        if gated and gateRole is None:
            await ctx.send('ERROR: Cannot set Gate Enabled when no Gate Role is defined!')
        else:
            self.configManager.setGateData(
                guild, gated, gateData.allow_rejoin, gateData.key_role_id, gateData.keyed_users)
            self.configManager.writeConfig()
            await ctx.send('Gate Enabled Set: ' + str(gated))

    @setGateEnabled.error
    async def setGateEnabled_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send('Invalid Entry! Usage: !setGateEnabled <True/False>')
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('ERROR! Usage: !setGateEnabled <true/false>')
        else:
            await ctx.send(error.args[0])

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def setGateRole(self, ctx, role: discord.Role):
        """Sets the Role granted to Keyed users"""
        guild = ctx.guild
        gateData = self.configManager.getGateData(guild)

        self.configManager.setGateData(
            guild, gateData.gate_enabled, gateData.allow_rejoin, role.id, gateData.keyed_users)
        self.configManager.writeConfig()
        await ctx.send("Setting Gated Role: @" + role.name)

    @setGateRole.error
    async def setGateRole_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send('Invalid Role! Usage: !setGateRole <role>')
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('ERROR! Usage: !setGateRole <role>')
        else:
            await ctx.send(error.args[0])

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def setGateRejoin(self, ctx, rejoin: bool):
        """Sets Gate Enabled for the server"""
        guild = ctx.guild
        gateData = self.configManager.getGateData(guild)
        gateRole = guild.get_role(gateData.key_role_id)

        if rejoin and gateRole is None:
            await ctx.send('ERROR: Cannot set Gate Rejoin when no Gate Role is defined!')
        elif rejoin and not gateData.gate_enabled:
            await ctx.send('ERROR: Cannot set Gate Rejoin when Gate is not Enabled!')
        else:
            self.configManager.setGateData(
                guild, True, rejoin, gateData.key_role_id, gateData.keyed_users)
            self.configManager.writeConfig()
            await ctx.send('Gate Enabled Set: ' + str(rejoin))

    @setGateRejoin.error
    async def setGateRejoin_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send('Invalid Entry! Usage: !setGateRejoin <True/False>')
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('ERROR! Usage: !setGateRejoin <true/false>')
        else:
            await ctx.send(error.args[0])

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def getMemberData(self, ctx, member: discord.Member):
        """Gets Account Data for a Guild Member"""
        guild = ctx.guild
        gateData = self.configManager.getGateData(guild)

        output = 'Account Data For User: ' + member.name + '#' + \
            member.discriminator + ' (' + str(member.id) + ')\n'
        output += 'Server Nickname: ' + member.display_name + '\n'

        forumAcct = gateData.keyed_users.get(member.id)

        if forumAcct is not None:
            output += 'Forum Account: https://forums.europeians.com/index.php/members/' + forumAcct

        await ctx.send(output)

    @getMemberData.error
    async def getMemberData_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send('Invalid User! Usage: !getMemberData <user>')
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('ERROR! Usage: !getMemberData <user>')
        else:
            await ctx.send(error.args[0])

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def registerMember(self, ctx, member: discord.Member, forumAccount: int):
        """Registers a Guild Member's forum account and grants the Gate Role"""
        guild = ctx.guild
        gateData = self.configManager.getGateData(guild)

        if not gateData.gate_enabled:
            await ctx.send('ERROR! Gate Enabled must be set to True before users can be registered.')
            return

        gateRole = guild.get_role(gateData.key_role_id)

        if gateRole is None:
            await ctx.send('ERROR! A valid Gate Role must be set before users can be registered.')
            return

        gateData.keyed_users[member.id] = forumAccount
        self.configManager.setGateData(
            guild, True, gateData.allow_rejoin, gateData.key_role_id, gateData.keyed_users)
        self.configManager.writeConfig()
        await member.add_roles(gateRole, reason='User Registered by ' + ctx.author.name)
        await ctx.send('User ' + str(member.id) + ' registered to forum account: https://forums.europeians.com/index.php/members/' + str(forumAccount))

    @registerMember.error
    async def registerMember_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send('Invalid User! Usage: !registerMember <user> <forumID>')
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('ERROR! Usage: !registerMember <user> <forumID>')
        else:
            await ctx.send(error.args[0])

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def unregisterMember(self, ctx, member: discord.Member):
        """Unregisters a Guild Member's forum account and removes the Gate Role"""
        guild = ctx.guild
        gateData = self.configManager.getGateData(guild)

        if gateData.keyed_users[member.id] is not None:
            del gateData.keyed_users[member.id]
            self.configManager.setGateData(
                guild, gateData.gate_enabled, gateData.allow_rejoin, gateData.key_role_id, gateData.keyed_users)
            self.configManager.writeConfig()

            gateRole = guild.get_role(gateData.key_role_id)
            if gateRole is not None:
                await member.remove_roles(gateRole, reason='Unregistered by ' + ctx.author.name)

        await ctx.send('Unregistered Member ' + member.name + '#' + member.discriminator)

    @unregisterMember.error
    async def unregisterMember_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send('Invalid User! Usage: !unregisterMember <user>')
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('ERROR! Usage: !unregisterMember <user>')
        else:
            await ctx.send(error.args[0])

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def updateConfig(self,  ctx):
        """Persists Config Data to Disk (performed automatically on shutdown)"""
        self.configManager.updateServerData(ctx.guild)
        self.configManager.writeConfig()
        await ctx.send('Server Data Updated!')
