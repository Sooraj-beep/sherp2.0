from .schedulebuddy import setup_schedule_buddy
from .kattis import setup_kattis
from .misc import setup_misc_cog 
from .snipe import setup_snipe 
from .prereq import setup_prereq



async def setup_all_cogs(bot, guilds):
    await setup_schedule_buddy(bot, guilds)
    await setup_kattis(bot, guilds)
    await setup_misc_cog(bot, guilds)
    await setup_snipe(bot, guilds)
    await setup_prereq(bot, guilds)
