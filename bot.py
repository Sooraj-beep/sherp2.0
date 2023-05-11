import discord
from discord.ext import commands
import json
from dotenv import load_dotenv
import os
import requests
from io import BytesIO
import random

import schedubuddy.schedule_session as schedule_session
from schedubuddy.draw_sched import draw_schedule

SHERP_ID = "212613981465083906"
SHERP_URL = "https://media.giphy.com/media/artj92V8o75VPL7AeQ/giphy.gif"
SCHEDUBUDDY_ROOT = 'https://schedubuddy1.herokuapp.com//api/v1/'
KATTIS_PROBLEM_URL = "https://open.kattis.com/problems/"
KATTIS_CONTEST_URL = "https://open.kattis.com/problem-sources/"

# load the .env file
load_dotenv()
# create a client with all intents
client = commands.Bot(command_prefix='?', intents=discord.Intents.all())

# ?sched plugin
schedule_session.setup(client)

# load commands.json
with open("knowledge/commands.json", "r", encoding='utf-8') as f:
    cmds = json.load(f)
with open("knowledge/copypasta.json", "r", encoding='utf-8') as f:
    pastas = json.load(f)
with open("knowledge/ualberta.ca.json", "r", encoding='utf-8') as f:
    catalog = json.load(f)
with open("knowledge/kattis.json", "r", encoding='utf-8') as f:
    kattis_links = json.load(f)
with open("knowledge/problems.json", "r", encoding='utf-8') as f:
    kattis_problems = json.load(f)
with open("knowledge/contests.json", "r", encoding='utf-8') as f:
    kattis_contests = json.load(f)
with open("knowledge/specific.json", "r", encoding='utf-8') as f:
    kattis_specific = json.load(f)

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
    elif "?prereq" in message.content:
        args = message.content.split(' ')
        if not 3 <= len(args) <= 4:
            await message.channel.send(f'Usage: `?prereq [department] [course]`, e.g. `?prereq cmput 229`')
            return
        dept = args[1] if len(args) == 3 else args[1] + ' ' + args[2]
        course = args[2] if len(args) == 3 else args[3]
        dept, course = dept.upper(), course.upper()
        if not dept in catalog['courses']:
            await message.channel.send(f'Could not find **{dept}**')
            return
        if not course in catalog['courses'][dept]:
            await message.channel.send(f'Could not find **{course}** in the {dept} department')
            return
        catalog_obj = catalog['courses'][dept][course]
        course_name = catalog_obj['name']
        prereqs = catalog_obj.get('raw', 'No prerequisites')
        await message.channel.send(f'**{dept} {course} - {course_name}**\n{prereqs}')
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
    elif "?kattis" in message.content:
        commands = []
        commands.extend(list(kattis_links.keys()))
        commands.extend(list(kattis_problems.keys()))
        more = ["problem", "contest", "contests", "rank", "specific"]
        commands.extend(more)

        args = message.content.split(' ')
        if len(args) != 2:
            await message.channel.send("Usage ?kattis <cmd>. For a list of commands use\n\t?kattis help")
            return
        cmd = args[1]

        if cmd == "help":
            out = ""
            out += "Commands:\n"
            for cmd in commands:
                out += '\t' + cmd + '\n'
            await message.channel.send(out)
            return
        elif cmd == "problem":
            problems = []
            for k in kattis_problems:
                problems.extend(kattis_problems[k])
            problem = random.choices(problems)[0]
            link = KATTIS_PROBLEM_URL + problem
            await message.channel.send(link)
            return
        else:
            if cmd in kattis_links:
                await message.channel.send(kattis_links[cmd])
                return
            elif cmd == "contest":
                contest = random.choices(kattis_contests["contests"])[0]
                link = KATTIS_CONTEST_URL + contest
                await message.channel.send(link)
                return
            elif cmd == "contests":
                contest = random.choices(kattis_contests["contests"])
                link = KATTIS_CONTEST_URL
                await message.channel.send(link)
                return
            elif cmd == "rank":
                link = 'https://open.kattis.com/ranklist'
                await message.channel.send(link)
                return
            elif cmd == "specific":
                out = "You can ask for a problem from one of the following topics:\n"
                for k in kattis_specific:
                    out += f'\t{k}\n'    
                await message.channel.send(out)
                return
            elif cmd in kattis_problems:
                problem = random.choices(kattis_problems[cmd])[0]
                link = KATTIS_PROBLEM_URL + problem
                await message.channel.send(link)
                return
            elif cmd in [k.split()[0] for k in kattis_specific]:
                for k in kattis_specific:
                    if cmd == k.split()[0]:
                        cmd = k
                problem = random.choices(kattis_specific[cmd])[0]
                link = KATTIS_PROBLEM_URL + problem
                await message.channel.send(link)
                return
            else:
                await message.channel.send("Usage ?kattis <cmd>. For a list of commands use\n\t?kattis help")
                return
    elif "?bbq23" in message.content:
        embed = discord.Embed(title="BBQ 23",color=3447003,description="Here's a bunch of gigachads together")
        embed.set_image(url="https://cdn.discordapp.com/attachments/968245983697842196/1101298256459346000/IMG_2316.jpg")
        await message.channel.send(embed=embed)
    
    await client.process_commands(message)


# run the bot using the token in the .env file
client.run(os.getenv("BOT_TOKEN"))
