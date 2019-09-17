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

    # async def on_message(self, message):
    #     ret = super(Bot, self).on_message(message)
    #     if message.author.id == CHARLIE_ID: # Charlie
    #         return ret
    #     # logger.debug("{}".format(message))
    #     if message.channel.id == BOT_LOBBY_CHANNEL: # bot-lobby
    #         if 'cat' in message.content.lower() or 'kitty' in message.content.lower():
    #             await message.add_reaction("🐈")
    #     return ret

    async def on_message_edit(self, before, after):
        fmt = '**{0.author}** edited their message:\n{0.content} -> {1.content}'
        channel = self.get_channel(BOT_DEBUG_CHANNEL)
        await channel.send(fmt.format(before, after))

    async def on_command_error(self, event, *args, **kwargs):
        logger.error('Connected!')
        channel = self.get_channel(BOT_DEBUG_CHANNEL)
        await channel.send("Command error: {}".format(event))

    async def on_error(self, event, *args, **kwargs):
        logger.error('Connected!')
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