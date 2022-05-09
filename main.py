import discord
from discord.ext import commands
from decouple import config
import requests
from table2ascii import table2ascii as t2a, PresetStyle

api_uri = "http://localhost:90"

bot = commands.Bot(command_prefix='!',
                   description='This is a test bot for TallerPrograma',
                   intents=discord.Intents.default())

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')

@bot.command()
async def ping(ctx):
    await ctx.send('pong')

@bot.command()
async def login(ctx):
    response = requests.post(f'{api_uri}/auth/login', {'name': 'Elk', 'password': config('DB_PASSWORD')})
    await ctx.send(f'Did I loggedIn? {response.ok}')

@bot.command()
async def tournaments(ctx):
    response = requests.get(f'{api_uri}/api/tournaments')
    response = response.json()

    message = ''
    for tournament in response:
        message += tournament['name'] + '\n'
    
    await ctx.send(f'Tournaments: \n{message}')

@bot.command()
async def ranking(ctx, name, page = 1):
    response = requests.get(f'{api_uri}/api/tournaments/{name}/leagues/global/ranking')
    response = response.json()

    if 'msg' in response and response['msg'] == 'Tournament not found':
        await ctx.send(f'Wrong tournament')
        return

    headers = ['Nom', 'Elo', 'Nº Partides']
    body = []
    for i in range(10):
        index = (page - 1) * 10 + i
        if index < len(response):
            player = response[index]
            body.append([player['user']['name'], player['elo'], player['n_games']])

    message = t2a(header=headers, body=body, style=PresetStyle.thin_compact)
    
    await ctx.send(f'```\n{message}\n```')

async def add_role_to_member(message, member, role):
    guild = message.guild
   
    discord_role = discord.utils.get(guild.roles, name = role)
    
    if not discord_role:
        discord_role = await guild.create_role(name=role, colour=discord.Colour.dark_blue())
    
    await member.add_roles(discord_role)

@bot.command()
async def role(ctx):
    emote1 = '🎟'
    emote2 = '🎫'

    message = await ctx.send(f'Add yourself to a competition\n-Click {emote1} to join AIChallange\n-Click {emote2} to join AIColiseum')

    await message.add_reaction(emote1)
    await message.add_reaction(emote2)

    def check(reaction, user):
        return user == ctx.author and str(
            reaction.emoji) in [emote1, emote2]

    while True:
        reaction, author = await bot.wait_for("reaction_add", check=check)

        if str(reaction.emoji) == emote1:
            await add_role_to_member(message, author, 'AIChallange')

        if str(reaction.emoji) == emote2:
            await add_role_to_member(message, author, 'AIColiseum')


@bot.command()
async def table(ctx):
    # In your command:
    output = t2a(
        header=["Rank asdasda", "Team", "Kills", "Position Pts", "Total"],
        body=[[1, 'Team A 1982y31923y12312', 2, 4, 6], [2, 'Team B', 3, 3, 6], [3, 'Team C', 4, 2, 6]],
        style=PresetStyle.thin_compact
    )

    await ctx.send(f"```\n{output}\n```")


bot.run(config('KEY'))
