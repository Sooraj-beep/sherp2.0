import discord
from discord.ext import commands
import json
from dotenv import load_dotenv
import os
import requests
from io import BytesIO
import random

import schedule_session
from draw_sched import draw_schedule

SHERP_ID = "212613981465083906"
SHERP_URL = "https://media.giphy.com/media/artj92V8o75VPL7AeQ/giphy.gif"
SCHEDUBUDDY_ROOT = 'https://schedubuddy1.herokuapp.com//api/v1/'

# load the .env file
load_dotenv()
# create a client with all intents
client = commands.Bot(command_prefix='?', intents=discord.Intents.all())

# ?sched plugin
schedule_session.setup(client)

# load commands.json
with open("commands.json", "r", encoding='utf-8') as f:
    cmds = json.load(f)
with open("copypasta.json", "r", encoding='utf-8') as f:
    pastas = json.load(f)

@client.event
async def on_message(message):
    # stops the bot from responding to itself
    if message.author.bot: return
    if message.content in cmds and message.content != "//":
        # if string return string, if list return random element
        if type(cmds[message.content]) == list:
            response = random.choice(cmds[message.content])
        else:
            response = cmds[message.content]
        await message.channel.send(SHERP_URL + response if message.author.id == SHERP_ID else response)
        return
    # find message.content in commands.json and append msg with the value
    elif "?pasta" in message.content:
        # pick a random copypasta from copypasta.json
        await message.channel.send(random.choice(pastas))
    elif "?view" in message.content:
        errmsg = ''
        try:
            args = message.content.split(' ')
            term = args[1]
            year = args[2]
            room = '%20'.join(args[3:]).upper()
            if term.lower() in ['f', 'fa', 'fall']: term = 'Fall'
            elif term.lower() in ['w', 'wi', 'win', 'wint', 'winter']: term = 'Winter'
            elif term.lower() in ['sp', 'spr', 'spring']: term = 'Spring'
            elif term.lower() in ['su', 'sum', 'summ', 'summer']: term = 'Summer'
            errmsg = "Enter a valid term, e.g. 'fall'"
            assert(term in ['Fall', 'Winter', 'Spring', 'Summer'])
            if year in ['2023', '23']: year = '2023'
            elif year in ['2024', '24']: year = '2024'
            errmsg = "Enter a valid year, e.g. '2024'"
            assert(year in ['2023', '2024'])
            termid = None
            if year == '2023':
                if term == 'Winter': termid = '1820'
                elif term == 'Spring': termid = '1830'
                elif term == 'Summer': termid = '1840'
                elif term == 'Fall': termid = '1850'
            elif year == '2024':
                if term == 'Winter': termid = '1860'
            errmsg = f"Could not find term {term} {year}"
            assert(termid)
        except:
            await message.channel.send(errmsg)
            return

        url = SCHEDUBUDDY_ROOT + f'room-sched/?term={termid}&room={room}'
        response = requests.get(url)
        if response.status_code == 200:
            data = json.loads(response.text)
            image = draw_schedule(data['objects']['schedules'][0])
            bufferedio = BytesIO()
            image.save(bufferedio, format="PNG")
            bufferedio.seek(0)
            file = discord.File(bufferedio, filename="image.png")
            await message.channel.send(file=file)
    
    await client.process_commands(message)


# run the bot using the token in the .env file
client.run(os.getenv("BOT_TOKEN"))
