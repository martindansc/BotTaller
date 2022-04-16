import discord
from discord.ext import commands
from decouple import config
import random

bot = commands.Bot(command_prefix='!',
                   description='My first python discord bot',
                   intents=discord.Intents.default())


@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))


@bot.command()
async def roll(ctx, number: int):
    """Random roll"""
    await ctx.send('{0.mention} rolled {1} / {2} '.format(ctx.author, random.randint(1, number), number))

bot.run(config('KEY'))
