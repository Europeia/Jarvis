import discord
from discord.ext import commands

from config import ConfigManager


class AdministrationCommands:
    bot = None
    configManager = None

    def __init__(self, bot, configMgr: ConfigManager):
        self.bot = bot
        self.configManager = configMgr

        commands = list()
        commands.append(self.addRole)
        commands.append(self.joinRole)
        commands.append(self.remRole)
        commands.append(self.leaveRole)
        commands.append(self.addRoleMgr)
        commands.append(self.remRoleMgr)
        commands.append(self.toggleJoinableRole)
        commands.append(self.listRoleData)
        commands.append(self.getGreetingMessage)
        commands.append(self.setGreetingMessage)
        commands.append(self.updateConfig)

        for iCmd in commands:
            if iCmd not in self.bot.commands:
                self.bot.add_command(iCmd)

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
                return
            if 'Member ' in error.args[0]:
                await ctx.send('Invalid Member! Usage: !addRole <role> <user>')
                return

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
                return
    
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
                return
            if 'Member ' in error.args[0]:
                await ctx.send('Invalid Member! Usage: !remRole <role> <user>')
                return

    @commands.command()
    @commands.guild_only()
    async def leaveRole(self, ctx, role: discord.Role):
        """Leaves a Joinable Role: !leaveRole <role>"""
        if not self.configManager.isJoinableRole(ctx.guild, role):
            await ctx.send('@' + role.name + ' isn\'t joinable.')
            return
        await ctx.author.add_roles(role, reason='Leaving a Joinable Role by ' + ctx.author.name)
        await ctx.send('Left @' + role.name)
    
    @leaveRole.error
    async def leaveRole_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            if 'Role ' in error.args[0]:
                await ctx.send('Invalid Role! Usage: !leaveRole <role>')
                return

    def is_admin():
        async def predicate(ctx):
            return ctx.author.guild_permissions.administrator
        return commands.check(predicate)

    @commands.command()
    @commands.guild_only()
    @is_admin()
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
                return
            if 'Member ' in error.args[0]:
                await ctx.send('Invalid Member! Usage: !addRoleMgr <role> <user>')
                return

    @commands.command()
    @commands.guild_only()
    @is_admin()
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
                return
            if 'Member ' in error.args[0]:
                await ctx.send('Invalid Member! Usage: !remRoleMgr <role> <user>')
                return

    @commands.command()
    @commands.guild_only()
    @is_admin()
    async def listRoleData(self, ctx, role: discord.Role):
        """Lists Role Data for a Role: !listRoleData <role>"""
        output = 'Config Data for Role - ' + role.name + ' : ' + str(role.id) + '\n'
        output += 'Joinable Group: ' + str(self.configManager.isJoinableRole(ctx.guild, role)) + '\n'
        
        commanders = self.configManager.listCommanders(ctx.guild, role)
        if len(commanders) < 1:
            commanders = 'None'
        output += 'Managers for @' + role.name + ':\n' + commanders
        
        await ctx.send(output)

    @listRoleData.error
    async def listRoleData_error(self, ctx, error):
        if isinstance(error,  commands.BadArgument):
            await ctx.send('Invalid Role! Usage: !listRoleData <role>')
    
    @commands.command()
    @commands.guild_only()
    @is_admin()
    async def toggleJoinableRole(self, ctx, role: discord.Role):
        """Makes a role Joinable by any user"""
        joinable = self.configManager.isJoinableRole(ctx.guild, role)
        self.configManager.setJoinableRole(ctx.guild, role, not joinable)
        await ctx.send('Joinable Group for @' + role.name + ' set to ' + str(not joinable))
    
    @toggleJoinableRole.error
    async def toggleJoinableRole_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send('Invalid Role! Usage: !toggleJoinablerole <role>')

    @commands.command()
    @commands.guild_only()
    @is_admin()
    async def setGreetingMessage(self, ctx, *, greetingMessage: str):
        """Sets the Greeting Message sent to all new members of the Server (set to 'none' to disable)"""
        self.configManager.setGreetingMessage(ctx.guild,  greetingMessage)
        await ctx.send('New Greeting Message Set!')

    @commands.command()
    @commands.guild_only()
    @is_admin()
    async def getGreetingMessage(self,  ctx):
        """Shows the Greeting Message sent to all new members of the server (if 'none' no message will be sent)"""
        await ctx.send(self.configManager.getGreetingMessage(ctx.guild))

    @commands.command()
    @commands.guild_only()
    @is_admin()
    async def updateConfig(self,  ctx):
        """Persists Config Data to Disk (performed automatically on shutdown)"""
        self.configManager.updateServerData(ctx.guild)
        self.configManager.writeConfig()
        await ctx.send('Server Data Updated!')
