import discord
from discord.ext.commands.bot import Bot
import asyncio
from config.secrets import *
from commands.basic import *
from commands.admin import *
from utils.checks import load_config
from systemd.journal import JournaldLogHandler
from utils.spiffyText import spiff
import logging

logger = logging.getLogger('discord')

# instantiate the JournaldLogHandler to hook into systemd
journald_handler = JournaldLogHandler()

logging.addLevelName(
    logging.DEBUG,
    spiff(logging.getLevelName(logging.DEBUG), 'yellow'))
logging.addLevelName(
    logging.INFO,
    spiff(logging.getLevelName(logging.INFO), 'cyan'))
logging.addLevelName(
    logging.WARNING,
    spiff(logging.getLevelName(logging.WARNING), 'yellow', 'b'))
logging.addLevelName(
    logging.ERROR,
    spiff(logging.getLevelName(logging.ERROR), 'red'))
logging.addLevelName(
    logging.CRITICAL,
    spiff(logging.getLevelName(logging.CRITICAL), 'red', 'b'))

logging_format = '[%(asctime)s] %(process)d-%(levelname)s '
logging_format += '%(module)s::%(funcName)s():%(lineno)d: '
logging_format += '%(message)s'
color_formatter = logging.Formatter(logging_format)

journald_handler.setFormatter(color_formatter)
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

    async def on_message(self, message):
        ret = super(Bot, self).on_message(message)
        if message.author.id == CHARLIE_ID: # Charlie
            return ret

        # if message.channel.id == BOT_LOBBY_CHANNEL: # bot-lobby
        #     if 'cat' in message.content.lower() or 'kitty' in message.content.lower():
        #         await message.add_reaction("🐈")

        if 'cat' in message.content.lower() or 'kitty' in message.content.lower():
            await message.add_reaction("🐈")

        if message.channel.id == SELMA_TEST_CHANNEL:
            pass

        await self.process_commands(message)                

    async def on_message_edit(self, before, after):
        fmt = '**{0.author}** edited their message:\n{0.content} -> {1.content}'
        channel = self.get_channel(BOT_DEBUG_CHANNEL)
        await channel.send(fmt.format(before, after))

    async def on_command_error(self, ctx, event):
        channel = self.get_channel(BOT_DEBUG_CHANNEL)
        log.error('{}'.format(ctx))
        log.error('{}'.format(event))
        try:
            await channel.send("Message: {}".format(event.message))
        except:
            logger.error("Failed with event.message")
        try:
            await channel.send("Command: {}".format(event.args))
        except:
            logger.error("Failed with event.args")
        try:
            await channel.send("Args: {}".format(event.kwargs))
        except:
            logger.error("Failed with event.kwargs")
        try:
            await channel.send("Kwargs: {}".format(event.command))
        except:
            logger.error("Failed with event.command")
        try:
            await channel.send("Channel: {}".format(event.channel))
        except:
            logger.error("Failed with event.channel")
        try:
            await channel.send("Invoker: {}".format(event.author))
        except:
            logger.error("Failed with event.author")
           

    async def on_error(self, event, *args, **kwargs):
        logger.error('{}'.format(event))
        channel = self.get_channel(BOT_DEBUG_CHANNEL)
        await channel.send("Error: {}".format(event))


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