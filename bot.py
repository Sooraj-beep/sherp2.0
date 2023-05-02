import discord
import json
from dotenv import load_dotenv
import os
import requests
from draw_sched import draw_schedule
from io import BytesIO
import random

SHERP_ID = "212613981465083906"
SHERP_URL = "https://media.giphy.com/media/artj92V8o75VPL7AeQ/giphy.gif"

# load the .env file
load_dotenv()
# create a client with all intents
client = discord.Client(intents=discord.Intents.all())
# load commands.json
with open("commands.json", "r", encoding='utf-8') as f:
    commands = json.load(f)


@client.event
async def on_message(message):
    # stops the bot from responding to itself
    if message.author.bot: return
    
    if message.content in commands and message.content != "//":
        # if string return string, if list return random element
        if type(commands[message.content]) == list:
            response = random.choice(commands[message.content])
        else:
            response = commands[message.content]
        await message.channel.send(SHERP_URL + response if message.author.id == SHERP_ID else response)
    # find message.content in commands.json and append msg with the value

    if "?view" in message.content:
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
            elif year == '2024':
                if term == 'Fall': termid = '1850'
                if term == 'Winter': termid = '1860'
            errmsg = f"Could not find term {term} {year}"
            assert(termid)
        except:
            await message.channel.send(errmsg)
            return

        schedubudy_root = 'https://schedubuddy1.herokuapp.com//api/v1/'
        url = schedubudy_root + f'room-sched/?term={termid}&room={room}'
        response = requests.get(url)
        if response.status_code == 200:
            data = json.loads(response.text)
            image = draw_schedule(data)
            bufferedio = BytesIO()
            image.save(bufferedio, format="PNG")
            bufferedio.seek(0)
            file = discord.File(bufferedio, filename="image.png")
            await message.channel.send(file=file)


# run the bot using the token in the .env file
client.run(os.getenv("BOT_TOKEN"))
