import discord
import json
from dotenv import load_dotenv
import os

SHERP_ID = "212613981465083906"
SHERP_URL = "https://media.giphy.com/media/artj92V8o75VPL7AeQ/giphy.gif"

# load the .env file
load_dotenv()
# create a client with all intents
client = discord.Client(intents=discord.Intents.all())
# load commands.json
with open("commands.json", "r") as f:
    commands = json.load(f)


@client.event
async def on_message(message):
    # stops the bot from responding to itself
    if message.author.bot: return
    
    if message.content in commands:
        response = commands[message.content]
        await message.channel.send(SHERP_URL + response if message.auther.id == SHERP_ID else response)

# run the bot using the token in the .env file
client.run(os.getenv("BOT_TOKEN"))
