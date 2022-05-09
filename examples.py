import discord
from discord.ext import commands
from decouple import config
import random
import pickledb
from geopy.geocoders import Nominatim
import requests
import json
import time

from table2ascii import table2ascii as t2a, PresetStyle


db = pickledb.load('db.db', False)

geolocator = Nominatim(user_agent="TallerPrograma")

bot = commands.Bot(command_prefix='!',
                   description='My first python discord bot',
                   intents=discord.Intents.default())

cache = {}

@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))

@bot.command()
async def ping(ctx):
     await ctx.send('pong')

@bot.command()
async def roll(ctx, number: int):
    """Random roll"""
    await ctx.send('{0.mention} rolled {1} / {2} '.format(ctx.author, random.randint(1, number), number))


@bot.command()
async def temperature(ctx, city='Barcelona'):
    """Get current temperature in city"""

    if city not in cache: 
        location = geolocator.geocode(city)
        cache[city] = location
    else:
        location = cache[city]

    response = requests.get(f'https://api.open-meteo.com/v1/forecast?latitude={location.latitude}&longitude={location.longitude}&current_weather=true')
    response = response.json()

    await ctx.send(f'Current weather in {city}: {response["current_weather"]}')

@bot.command(name='create-channel')
async def create_channel(ctx, channel_name='real-python'):
    guild = ctx.guild
    existing_channel = discord.utils.get(guild.channels, name=channel_name)
    if not existing_channel:
        print(f'Creating a new channel: {channel_name}')
        await guild.create_text_channel(channel_name)

@bot.command(name='get-role')
async def get_role(ctx, role='stupid'):
    guild = ctx.guild
    existing_role = discord.utils.get(guild.roles, name=role)
    if not existing_role:
        existing_role = await guild.create_role(name=role, colour=discord.Colour.green())
    await ctx.author.add_roles(existing_role)
    await ctx.send(f'{ctx.author.mention} You are now part of the {role} community')


@bot.command()
async def yesOrNo(ctx):
    emojis = ['👎', '👍']
    message = await ctx.send("Yes or no?")
    for emoji in emojis:
        await message.add_reaction(emoji)
    time.sleep(20)
    #todo
    await ctx.send(f"Yes won")
    

@bot.command()
async def add_one(ctx):
    counter = db.get('counter')
    if counter == False:
        counter = 1
    else:
        counter += 1
    
    db.set('counter', counter)
    db.dump()

    await ctx.send(f'Thanks for increasing the useless counter. The cunter current value is {counter}')

async def reset(ctx):
    db.rem('counter')
    db.dump()
    await ctx.send(f'The counter went to 0 :(')

@bot.event
async def on_member_join(member):
    await member.create_dm()
    await member.dm_channel.send(
        f'Hi {member.name}, welcome to my Discord server!'
    )

@bot.command()
async def ranking(ctx, tournament):
    r1 = requests.post('http://localhost:8081/auth/login', {'name': 'Elk', 'password': config('DB_PASSWORD')})
    if r1.ok:
        response = (requests.get(f'http://localhost:8081/api/tournaments/{tournament}/leagues/global/ranking', cookies=r1.cookies))
        response = response.json()

    await ctx.send(f'{response}')

@bot.command()
async def tournaments(ctx):
    r1 = requests.post('http://localhost:8081/auth/login', {'name': 'Elk', 'password': config('DB_PASSWORD')})
    if r1.ok:
        response = (requests.get('http://localhost:8081/api/tournaments', cookies=r1.cookies))
        response = response.json()

    await ctx.send(f'{response}')

@bot.command()
async def table(ctx):
    # In your command:
    output = t2a(
        header=["Rank", "Team", "Kills", "Position Pts", "Total"],
        body=[[1, 'Team A', 2, 4, 6], [2, 'Team B', 3, 3, 6], [3, 'Team C', 4, 2, 6]],
        style=PresetStyle.thin_compact
    )

    await ctx.send(f"```\n{output}\n```")

bot.run(config('KEY'))
