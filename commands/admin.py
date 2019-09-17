import discord
import asyncio
import random
from discord.ext import commands
from discord.utils import get
from utils.checks import *

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["mute", "silence", "doom"])
    @commands.has_role("Vanir")
    async def hellfire(self, ctx, member: discord.Member):
        if member.id == 189761449013280768:
            await ctx.send("No.")
            return

        role = get(member.guild.roles, name='Eljudne')

        print(role)

        await member.add_roles(role)

    @commands.command(pass_context=True, aliases=['reboot'])
    async def restart(self, ctx):
        """Restarts the bot."""
        def check(msg):
            if msg:
                return (msg.content.lower().strip() == 'y' or msg.content.lower().strip() == 'n') and msg.author == self.bot.user
            else:
                return False

        latest = update_bot(True)
        if latest:
            await ctx.send('There is an update available for the bot.')
        #     reply = await self.bot.wait_for("message", check=check)
        #     with open('restart.txt', 'w', encoding="utf8") as re:
        #         re.write(str(ctx.message.channel.id))
            g = git.cmd.Git(working_dir=os.getcwd())
            g.execute(["git", "pull", "origin", "master"])
            try:
                await ctx.send(content=None, embed=latest)
            except:
                pass
            with open('quit.txt', 'w', encoding="utf8") as q:
                q.write('update')
            print('Downloading update and restarting...')
            await ctx.send('Downloading update and restarting (check your console to see the progress)...')

        else:
            print('Restarting...')
            with open('restart.txt', 'w', encoding="utf8") as re:
                re.write(str(ctx.message.channel.id))
            await ctx.send('Restarting...')

        # if self.bot.subpro:
        #     self.bot.subpro.kill()
        os._exit(0)