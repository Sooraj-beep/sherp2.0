# NO BS CODE AHEAD! This is the first and last comment you're getting. Good luck figuring everything out.
import discord
from discord.ext import commands

from helper import get_config

__DEFAULT_EMOJI_STR = "<:ban:939740396286791741>"
__DEFAULT_THRESHOLD = 5
__DEFAULT_IGNORED_CHANNELS = [882731509553987717, 403057458299404289, 402891511991369742, 788501054077009981, 800858183799013376]
__cfg = get_config().get("votedelete", None)

VOTEDELETE_EMOJI_STR = (
    __cfg.get("emoji", __DEFAULT_EMOJI_STR) if __cfg else __DEFAULT_EMOJI_STR
)

VOTEDELETE_THRESHOLD = (
    __cfg.get("threshold", __DEFAULT_THRESHOLD) if __cfg else __DEFAULT_THRESHOLD
)
IGNORED_CHANNELS = (
    __cfg.get("ignored_channels", __DEFAULT_IGNORED_CHANNELS) if __cfg else __DEFAULT_IGNORED_CHANNELS
)

class VoteDelete(commands.Cog):
    def __init__(self, bot: discord.Client):
        self.votedelete_emoji_str = VOTEDELETE_EMOJI_STR
        self.threshold = VOTEDELETE_THRESHOLD
        self.ignored_channels = IGNORED_CHANNELS
        self.bot = bot
    async def cog_load(self):
        await super().cog_load()
        print("VoteDelete loaded.")
    
    def checks(self, reaction):
        if str(reaction.emoji) != self.votedelete_emoji_str:
            return False
        message = reaction.message
        if reaction.count <= self.threshold:
            return False
        if message.channel.id in self.ignored_channels:
            return False
        return True

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        message = reaction.message
        if self.checks(reaction):
            try:
                await message.delete()
            except discord.Forbidden:
                print("Permissions aren't configured correctly.")
            except discord.NotFound:
                pass

async def setup_votedelete(bot, guilds):
    await bot.add_cog(VoteDelete(bot), guilds=guilds)