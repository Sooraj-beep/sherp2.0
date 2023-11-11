import discord
from discord.ext import commands
import json
from dotenv import load_dotenv
import os
import random

from helper import get_config

from cogs import setup_all_cogs
from typing import Optional


SHERP_ID = "212613981465083906"
SHERP_URL = "https://media.giphy.com/media/artj92V8o75VPL7AeQ/giphy.gif"
__DEFAULT_GUILDS = [402891511991369740]  # UAlberta CS server ID

# load the .env file
load_dotenv()
# create a client with all intents
app_id = os.getenv("DISCORD_APP_ID")

client = commands.Bot(
    command_prefix="?", intents=discord.Intents.all(), application_id=app_id
)


__cfg = get_config().get("general", None)
GUILDS = (
    [discord.Object(id=gid) for gid in __cfg.get("guild_ids", __DEFAULT_GUILDS)]
    if __cfg
    else __DEFAULT_GUILDS
)


@client.event
async def on_ready():
    await setup_all_cogs(client, GUILDS)


# load commands.json
with open("data/commands.json", "r", encoding="utf-8") as f:
    cmds = json.load(f)
with open("data/copypasta.json", "r", encoding="utf-8") as f:
    pastas = json.load(f)


# A command is trivial if its response is static string. These commands can
# defined in a single file along with their responses.
def is_trivial_command(c: str) -> Optional[str]:
    cmd = c.strip()
    if not cmd.startswith("?"):
        return None
    if cmd.count(" "):
        return None

    return cmds.get(cmd.lower(), None)


@client.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return

    if resp := is_trivial_command(message.content):
        await message.channel.send(resp)
        return

    elif "?pasta" in message.content:
        # pick a random copypasta from copypasta.json
        await message.channel.send(random.choice(pastas))
    await client.process_commands(message)


# run the bot using the token in the .env file
client.run(os.getenv("BOT_TOKEN"))
