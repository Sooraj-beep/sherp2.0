import discord
from discord.ext import commands
from datetime import datetime, timedelta
import json
from dotenv import load_dotenv
import os
import requests
from io import BytesIO
import random

import schedubuddy.schedule_session as schedule_session
import util
from schedubuddy.draw_sched import draw_schedule


SHERP_ID = "212613981465083906"
SHERP_URL = "https://media.giphy.com/media/artj92V8o75VPL7AeQ/giphy.gif"
SCHEDUBUDDY_ROOT = 'https://schedubuddy1.herokuapp.com//api/v1/'
KATTIS_PROBLEM_URL = "https://open.kattis.com/problems/"
KATTIS_CONTEST_URL = "https://open.kattis.com/problem-sources/"
SNIPE_TIMER = 10 # seconds

# load the .env file
load_dotenv()
# create a client with all intents
client = commands.Bot(command_prefix='?', intents=discord.Intents.all())

# ?sched plugin
schedule_session.setup(client)

# starboard
starboard_messages = {}
EMOJI_DISPLAY = "<:OnPhone:1062142401973588039>"
MIN_STARS_REQUIRED = 3
STARBOARD_CHANNEL_ID = 1133260871049691257
STARBOARD_CHANNEL = None
STARBOARD_MESSAGE_ID = None
TITLE = None

async def update_title(reaction_count, message):
    global TITLE
    TITLE = EMOJI_DISPLAY + f" x **{reaction_count}** |{message.channel.mention}"

@client.event
async def on_reaction_add(reaction, user):
    global STARBOARD_CHANNEL, STARBOARD_MESSAGE_ID
    if str(reaction.emoji) == EMOJI_DISPLAY:
        message = reaction.message
        is_not_system_message = message.type == discord.MessageType.default
        STARBOARD_CHANNEL = client.get_channel(STARBOARD_CHANNEL_ID)
        STARBOARD_MESSAGE_ID = starboard_messages.get(message.id)
        if not message.author.bot and not message.channel.is_nsfw():
            if reaction.count >= MIN_STARS_REQUIRED and message.id not in starboard_messages:
                #creates the title, content and embed for the message
                await update_title(reaction.count, message)
                starboard_content =  f"{message.content if is_not_system_message else message.system_content}\n\n"
                starboard_content += f"[Jump to Message!]({message.jump_url})"
                embed = discord.Embed(description=starboard_content, color=discord.Color.dark_green())
                embed.set_author(name=message.author.display_name, icon_url=message.author.avatar_url)
                if 0.0 == random.random(): embed.set_footer(text="<:peepSelfie:1066954556753330236>")
                #check for attachments
                if message.attachments:
                    for attachment in message.attachments:
                        if attachment.url.lower().endswith(("png", "jpeg", "jpg", "gif", "webp")):
                            embed.set_image(url=attachment.url)
                starboard_message = await STARBOARD_CHANNEL.send(TITLE, embed=embed)
                starboard_messages[message.id] = starboard_message.id
            #update the reaction count if more get added after posting
            elif reaction.count >= MIN_STARS_REQUIRED and message.id in starboard_messages:
                if STARBOARD_MESSAGE_ID:
                    await update_title(reaction.count, message)
                    starboard_message = await STARBOARD_CHANNEL.fetch_message(STARBOARD_MESSAGE_ID)
                    embed = starboard_message.embeds[0]
                    await starboard_message.edit(content=TITLE, embed=embed)
@client.event
async def on_reaction_remove(reaction, user):
    message = reaction.message
    #update the reaction count if :OnPhone: gets removed
    #needed to set this variable again otherwise there is an error when reaction.count == 0
    STARBOARD_MESSAGE_ID = starboard_messages.get(message.id)
    if str(reaction.emoji) == EMOJI_DISPLAY and message.id in starboard_messages:
        await update_title(reaction.count, message)
        starboard_message = await STARBOARD_CHANNEL.fetch_message(STARBOARD_MESSAGE_ID)
        embed = starboard_message.embeds[0]
        await starboard_message.edit(content=TITLE, embed=embed)
        
# load commands.json
with open("data/commands.json", "r", encoding='utf-8') as f:
    cmds = json.load(f)
with open("data/copypasta.json", "r", encoding='utf-8') as f:
    pastas = json.load(f)
with open("data/ualberta.ca.json", "r", encoding='utf-8') as f:
    catalog = json.load(f)
with open("data/kattis.json", "r", encoding='utf-8') as f:
    kattis_links = json.load(f)
with open("data/problems.json", "r", encoding='utf-8') as f:
    kattis_problems = json.load(f)
with open("data/contests.json", "r", encoding='utf-8') as f:
    kattis_contests = json.load(f)
with open("data/specific.json", "r", encoding='utf-8') as f:
    kattis_specific = json.load(f)

##### ?snipe
class DeletedMsg:
    def __init__(self, msg, attachment_path=None):
        self.msg = msg
        self.attachment_path = attachment_path
        self.time = datetime.utcnow()

deleted_messages = {} # {channel id : DeletedMsg}

@client.event
async def on_message_delete(message):
    attachment_path = None
    if message.attachments:
        attachment_path = await util.save_attachment(message.attachments[0])
    deleted_messages[message.channel.id] = DeletedMsg(message, attachment_path)
    if message.id in starboard_messages:
        #gets starboard channel and fetches the bots message that matches the deleted message's id
        msg = await STARBOARD_CHANNEL.fetch_message(starboard_messages[message.id])
        await msg.delete()
        del starboard_messages[message.id]

@client.command(name='snipe')
async def snipe(ctx):
    snipeTime = datetime.utcnow()
    deletedmsg = deleted_messages.pop(ctx.channel.id, None)
    if not deletedmsg or snipeTime - deletedmsg.time > timedelta(seconds=SNIPE_TIMER):
        await ctx.send(f"Nothing found")
        return
    embed = discord.Embed(description=f"**{deletedmsg.msg.author.name}** said: {deletedmsg.msg.content}", color=0x00ff00)
    if deletedmsg.attachment_path:
        file = discord.File(deletedmsg.attachment_path, filename=deletedmsg.attachment_path.split("/")[-1])
        embed.set_image(url=f"attachment://{file.filename}")
        await ctx.send(embed=embed, file=file)
    else:
        await ctx.send(embed=embed)

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
    elif "?desc" in message.content:
        args = message.content.split(' ')
        if not 3 <= len(args) <= 4:
            await message.channel.send(f'Usage: `?desc [department] [course]`, e.g. `?desc cmput 229`')
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
        if not 'desc' in catalog['courses'][dept][course]:
            await message.channel.send(f'There is no available course description for **{dept} {course}**.')
            return
        catalog_obj = catalog['courses'][dept][course]
        course_name = catalog_obj['name']
        course_faculty = catalog_obj['faculty']
        course_desc = catalog_obj['desc']
        await message.channel.send(f'**{dept} {course} - {course_name}**\n{course_faculty}\n{course_desc}')
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
    
    elif "?java" in message.content:
        embed = discord.Embed(title="Java",color = 3447003,description="Have you tried Kotlin?")
        embed.set_image(url="https://cdn.discordapp.com/attachments/968245983697842196/1101253691392143410/41BDFE8C-2BC0-4E2B-A3C9-539962B71707.jpg")
        await message.channel.send(embed=embed)


    await client.process_commands(message)


# run the bot using the token in the .env file
client.run(os.getenv("BOT_TOKEN"))
