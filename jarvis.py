import discord
import asyncio
from discord import message
# import logging

from discord.ext import commands

from config.file_config import FileConfigManager
from admin import AdministrationCommands

# logger = logging.getLogger('discord')
# logger.setLevel(logging.DEBUG)
# handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
# handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
# logger.addHandler(handler)

intents = discord.Intents.default()
intents.members = True
intents.presences = True
description = "J.A.R.V.I.S is an administration helper."
bot = commands.Bot(command_prefix='!', description=description, intents=intents)
configManager = None


@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------ Servers ------')
    global configManager
    configManager = FileConfigManager()
    updateConfigs()
    bot.add_cog(AdministrationCommands(bot,  configManager))

@bot.event
async def on_message(message: discord.Message):
    # do stuff
    if message.type == discord.MessageType.new_member : # Send a Greeting?
        guild = message.guild
        channel = message.channel
        author = message.author
        greeting = configManager.getGreetingMessage(guild)
        if greeting != 'none' :
            await asyncio.sleep(3)
            await channel.send(greeting.replace('@@NAME@@', author.mention))
        # Allow Rejoin, yo.

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
    await bot.close()
    quit()

try:
    f = open('token.txt',  'r')
except:
    print('Unable to find token.txt!')
    quit()

token = f.read().strip()
f.close()
print('Starting with Token: |' + token + '|')
bot.run(str(token))
