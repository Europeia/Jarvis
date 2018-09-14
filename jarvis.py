import discord

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
    print('------ Servers ------')
    global configManager
    configManager = ConfigManager()
    updateConfigs()
    AdministrationCommands(bot,  configManager)

@bot.event
async def on_message(message: discord.Message):
    # do stuff
    if message.type == discord.MessageType.new_member : # Send a Greeting?
        guild = message.guild
        channel = message.channel
        author = message.author
        greeting = configManager.getGreetingMessage(guild)
        if greeting != 'none' :
            await channel.send(greeting.replace('@@NAME@@', author.mention))

    await bot.process_commands(message)

def updateConfigs():
    servers = list(bot.guilds)
    global configManager
    for iServer in range(len(servers)):
        server = servers[iServer]
        configManager.updateServerData(server)
        print('Updated Data for ' + server.name + ':' + str(server.id))
    configManager.writeConfig()
    print('Updated Config Data Written!')


@bot.command()
@commands.is_owner()
async def shutdown(ctx):
    await ctx.message.author.send('Shutting Down!')
    await bot.logout()
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
