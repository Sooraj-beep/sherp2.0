import discord
from discord.ext import commands
from datetime import datetime, timedelta
import json
from dotenv import load_dotenv
import os
import requests
from io import BytesIO
import random

import util

from cogs import setup_all_cogs


SHERP_ID = "212613981465083906"
SHERP_URL = "https://media.giphy.com/media/artj92V8o75VPL7AeQ/giphy.gif"
SCHEDUBUDDY_ROOT = "https://schedubuddy1.herokuapp.com//api/v1/"
KATTIS_PROBLEM_URL = "https://open.kattis.com/problems/"
KATTIS_CONTEST_URL = "https://open.kattis.com/problem-sources/"
SNIPE_TIMER = 10  # seconds

# load the .env file
load_dotenv()
# create a client with all intents
app_id = os.getenv("DISCORD_APP_ID")

client = commands.Bot(
    command_prefix="?", intents=discord.Intents.all(), application_id=app_id
)

# starboard
starboard_messages = {}
EMOJI_DISPLAY = "<:OnPhone:1062142401973588039>"
MIN_STARS_REQUIRED = 3
STARBOARD_CHANNEL_ID = 1133260871049691257
STARBOARD_CHANNEL = None
STARBOARD_MESSAGE_ID = None
TITLE = None


GUILDS = [discord.Object(id=1137183815949881357), discord.Object(id=402891511991369740)]


async def update_title(reaction_count, message):
    global TITLE
    TITLE = EMOJI_DISPLAY + f" x **{reaction_count}** |{message.channel.mention}"


@client.event
async def on_ready():
    await setup_all_cogs(client, GUILDS)


@client.event
async def on_reaction_add(reaction, user):
    global STARBOARD_CHANNEL, STARBOARD_MESSAGE_ID
    if str(reaction.emoji) == EMOJI_DISPLAY:
        message = reaction.message
        is_not_system_message = message.type == discord.MessageType.default
        STARBOARD_CHANNEL = client.get_channel(STARBOARD_CHANNEL_ID)
        STARBOARD_MESSAGE_ID = starboard_messages.get(message.id)
        if not message.author.bot and not message.channel.is_nsfw():
            if (
                reaction.count >= MIN_STARS_REQUIRED
                and message.id not in starboard_messages
            ):
                # creates the title, content and embed for the message
                await update_title(reaction.count, message)
                starboard_content = f"{message.content if is_not_system_message else message.system_content}\n\n"
                starboard_content += f"[Jump to Message!]({message.jump_url})"
                embed = discord.Embed(
                    description=starboard_content, color=discord.Color.dark_green()
                )
                embed.set_author(
                    name=message.author.display_name, icon_url=message.author.avatar_url
                )
                if 0.0 == random.random():
                    embed.set_footer(text="<:peepSelfie:1066954556753330236>")
                # check for attachments
                if message.attachments:
                    for attachment in message.attachments:
                        if attachment.url.lower().endswith(
                            ("png", "jpeg", "jpg", "gif", "webp")
                        ):
                            embed.set_image(url=attachment.url)
                starboard_message = await STARBOARD_CHANNEL.send(TITLE, embed=embed)
                starboard_messages[message.id] = starboard_message.id
            # update the reaction count if more get added after posting
            elif (
                reaction.count >= MIN_STARS_REQUIRED
                and message.id in starboard_messages
            ):
                if STARBOARD_MESSAGE_ID:
                    await update_title(reaction.count, message)
                    starboard_message = await STARBOARD_CHANNEL.fetch_message(
                        STARBOARD_MESSAGE_ID
                    )
                    embed = starboard_message.embeds[0]
                    await starboard_message.edit(content=TITLE, embed=embed)


@client.event
async def on_reaction_remove(reaction, user):
    message = reaction.message
    # update the reaction count if :OnPhone: gets removed
    # needed to set this variable again otherwise there is an error when reaction.count == 0
    STARBOARD_MESSAGE_ID = starboard_messages.get(message.id)
    if str(reaction.emoji) == EMOJI_DISPLAY and message.id in starboard_messages:
        await update_title(reaction.count, message)
        starboard_message = await STARBOARD_CHANNEL.fetch_message(STARBOARD_MESSAGE_ID)
        embed = starboard_message.embeds[0]
        await starboard_message.edit(content=TITLE, embed=embed)


# load commands.json
with open("data/commands.json", "r", encoding="utf-8") as f:
    cmds = json.load(f)
with open("data/copypasta.json", "r", encoding="utf-8") as f:
    pastas = json.load(f)
with open("data/ualberta.ca.json", "r", encoding="utf-8") as f:
    catalog = json.load(f)


@client.event
async def on_message_delete(message):
    if message.id in starboard_messages:
        # gets starboard channel and fetches the bots message that matches the deleted message's id
        msg = await STARBOARD_CHANNEL.fetch_message(starboard_messages[message.id])
        await msg.delete()
        del starboard_messages[message.id]


@client.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return
    if message.content in cmds and message.content != "//":
        # if string return string, if list return random element
        if type(cmds[message.content]) == list:
            response = random.choice(cmds[message.content])
        else:
            response = cmds[message.content]
        await message.channel.send(
            SHERP_URL + response if message.author.id == SHERP_ID else response
        )
        return
    # find message.content in commands.json and append msg with the value
    elif "?pasta" in message.content:
        # pick a random copypasta from copypasta.json
        await message.channel.send(random.choice(pastas))
    await client.process_commands(message)


# run the bot using the token in the .env file
client.run(os.getenv("BOT_TOKEN"))
