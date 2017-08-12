import discord
from discord.ext import commands

from config import ConfigManager

class AdministrationCommands:
    bot = None
    configManager = None
   
    def __init__(self, bot, configMgr: ConfigManager):
        self.bot = bot
        self.configManager = configMgr
        self.bot.add_command(self.addRole)
        self.bot.add_command(self.remRole)
        self.bot.add_command(self.addCommander)
        self.bot.add_command(self.remCommander)

    @commands.command()
    @commands.guild_only()
    async def addRole(self, ctx, role: discord.Role,  member: discord.Member):
        if not (
            self.configManager.isCommander(ctx.guild,  role,  ctx.author) or 
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
    async def addRole_error(self, ctx,  error):
        if isinstance(error,  commands.BadArgument):
            if 'Role ' in error.args[0]:
                await ctx.send('Invalid Role! Usage: !addRole <role> <user>')
                return
            if 'Member ' in error.args[0]:
                await ctx.send('Invalid Member! Usage: !addRole <role> <user>')
                return

    @commands.command()
    @commands.guild_only()
    async def remRole(self, ctx,  role: discord.Role,  member: discord.Member):
        if not (
            self.configManager.isCommander(ctx.guild,  role,  ctx.author) or 
            (
                ctx.author.guild_permissions.manage_roles and 
                ctx.author.top_role.position >= role.position
            )
        ):
            await ctx.send("You don't have permission to add users to roles!")
            return
        await member.add_roles(role, reason='Removed by ' + ctx.author.name)
        await ctx.send('Removed ' + member.name + ' from @' + role.name)

    @remRole.error
    async def remRole_error(self,  ctx,  error):
        if isinstance(error,  commands.BadArgument):
            if 'Role ' in error.args[0]:
                await ctx.send('Invalid Role! Usage: !remRole <role> <user>')
                return
            if 'Member ' in error.args[0]:
                await ctx.send('Invalid Member! Usage: !remRole <role> <user>')
                return
    
    def is_admin():
        async def predicate(ctx):
            return ctx.author.guild_permissions.administrator
        return commands.check(predicate)
    
    @commands.command()
    @commands.guild_only()
    @is_admin()
    async def addCommander(self,  ctx,  role: discord.Role,  member: discord.Member):
        self.configManager.addCommander(ctx.guild,  role,  member);
        self.configManager.writeConfig()
        await ctx.send(member.name + ' can now add users to ' + role.name)

    @addCommander.error
    async def addCommander_error(self,  ctx,  error):
        if isinstance(error,  commands.BadArgument):
            if 'Role ' in error.args[0]:
                await ctx.send('Invalid Role! Usage: !addCommander <role> <user>')
                return
            if 'Member ' in error.args[0]:
                await ctx.send('Invalid Member! Usage: !addCommander <role> <user>')
                return
    
    @commands.command()
    @commands.guild_only()
    @is_admin()
    async def remCommander(self,  ctx,  role: discord.Role,  member: discord.Member):
        self.configManager.remCommander(ctx.guild,  role,  member);
        self.configManager.writeConfig()
        await ctx.send(member.name + ' can no longer add users to ' + role.name)

    @remCommander.error
    async def remCommander_error(self,  ctx,  error):
        if isinstance(error,  commands.BadArgument):
            if 'Role ' in error.args[0]:
                await ctx.send('Invalid Role! Usage: !remCommander <role> <user>')
                return
            if 'Member ' in error.args[0]:
                await ctx.send('Invalid Member! Usage: !remCommander <role> <user>')
                return
    
