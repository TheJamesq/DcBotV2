import discord
from discord.ext import commands
import os

#import all of the cogs
from help_cog import help_cog
from music_cog import music_cog

intents = discord.Intents.all()

bot = commands.Bot(command_prefix='.', intents=intents)
#remove the default help command so that we can write out own
bot.remove_command('help')

async def setup():
    bot.add_cog(help_cog(bot))
    bot.add_cog(music_cog(bot))

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')
    await setup()

#start the bot with our token
bot.run("MTE2MDY2MDQyODQ1MjUyODE3MA.GhnmNM.Tas4RxJ6vzhuEZ7BHJrObdy9QKmXpyAN-FqKrc")