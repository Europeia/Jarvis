from discord.ext import commands

from config import ConfigManager
from admin import AdministrationCommands

description = "J.A.R.V.I.S is an administration helper."
bot = commands.Bot(command_prefix='!', description=description)
configManager = None

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')
    global configManager
    configManager = ConfigManager()
    updateConfigs()
    AdministrationCommands(bot,  configManager)


def updateConfigs():
    servers = list(bot.guilds)
    global configManager
    for iServer in range(len(servers)):
        configManager.updateServerData(servers[iServer])
    configManager.writeConfig()
   
@bot.command()
@commands.is_owner()
async def shutdown(ctx):
    await ctx.message.author.send('Shutting Down!')
    bot.logout()
    exit()

try:    
    f = open('token.txt',  'r')
except:
    print('Unable to find token.txt!')
    exit()

token = f.read().strip()
f.close()
print('Starting with Token: |' + token + '|')
bot.run(str(token))
