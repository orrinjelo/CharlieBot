import discord
from discord.ext.commands.bot import Bot
import asyncio
from config.secrets import *
from commands.basic import *
from commands.admin import *
from utils.checks import load_config
from systemd.journal import JournaldLogHandler
import logging

logger = logging.getLogger('discord')
# get an instance of the logger object this module will use
logger = logging.getLogger(__name__)

# instantiate the JournaldLogHandler to hook into systemd
journald_handler = JournaldLogHandler()

# set a formatter to include the level name
journald_handler.setFormatter(logging.Formatter(
    '[%(levelname)s] %(message)s'
))

# add the journald handler to the current logger
logger.addHandler(journald_handler)
logger.setLevel(logging.DEBUG)

class SirCharles(Bot):
    async def on_ready(self):
        logger.info('Connected!')
        logger.info('Username: {0.name}\nID: {0.id}'.format(self.user))
        channel = self.get_channel(BOT_DEBUG_CHANNEL)
        await channel.send("I'm alive!")        

    async def on_member_join(self, member):
        guild = member.guild
        if guild.system_channel is not None:
            to_send = 'Welcome {0.mention} to {1.name}!'.format(member, guild)
            await guild.system_channel.send(to_send)

    async def on_message_edit(self, before, after):
        fmt = '**{0.author}** edited their message:\n{0.content} -> {1.content}'
        channel = self.get_channel(BOT_DEBUG_CHANNEL)
        await channel.send(fmt.format(before, after))

    async def on_error(self, event, *args, **kwargs):
        logger.error('Connected!')
        channel = self.get_channel(BOT_DEBUG_CHANNEL)
        await channel.send("{}".format(event))        


bot = SirCharles(load_config()['cmd_prefix'])

bot.add_cog(Basic(bot))
bot.add_cog(Admin(bot))

@bot.command()
async def add(ctx, left: int, right: int):
    """Adds two numbers together."""
    await ctx.send(left + right)

@bot.command()
async def editme(ctx):
    msg = await ctx.message.channel.send('10')
    await asyncio.sleep(3.0)
    await msg.edit(content='40')    

bot.run(API_KEY)