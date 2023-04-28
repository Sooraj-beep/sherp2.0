import discord
import json
from dotenv import load_dotenv
import os

SHERP_ID = "212613981465083906"

# load the .env file
load_dotenv()
# create a client with all intents
client = discord.Client(intents=discord.Intents.all())
# load commands.json
with open("commands.json", "r") as f:
    commands = json.load(f)


@client.event
async def on_message(message):
    # find message.content in commands.json and append msg with the value
    for command in commands:
        if message.content == command:
            msg = commands[command]

            # if the message is from sherps, add a celebratory gif
            if message.author.id == SHERP_ID:
                msg = "https://media.giphy.com/media/artj92V8o75VPL7AeQ/giphy.gif " + msg

            await message.channel.send(msg)


# run the bot using the token in the .env file
client.run(os.getenv("BOT_TOKEN"))
