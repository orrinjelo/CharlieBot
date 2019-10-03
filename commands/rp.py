import discord
import asyncio
import random
import aiohttp
import re
from discord.ext import commands
from config.secrets import *
from utils.checks import embed_perms, cmd_prefix_len
import logging
from urllib import parse
from urllib.request import Request, urlopen
from pymongo import MongoClient
from datetime import datetime as dt

logger = logging.getLogger('discord')

class Roleplay(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.session = aiohttp.ClientSession(loop=self.bot.loop, headers={"User-Agent": "AppuSelfBot"})
        self.mongo_client = MongoClient()
        self.xp_db = self.mongo_client['xp']
        self.xp = self.xp_db.xp

    async def log_post(self, message):
        player_id = hash(message.author)
        res = self.xp.find_one(
            {
                'id': player_id
            }
        )
        if not res:
            res = await self.create_xp(ctx)
        
        player_hist = res['history']
        player_hist.append(
            {
                'date': dt.now(),
                'message': message
            }
        )

        self.xp.update_one(
            {
                'id': player_id
            },
            {
                'history': player_hist
            }
        )

    async def create_xp(self, ctx):
        player_id = hash(ctx.message.author)
        player_name = str(ctx.message.author)
        ret = {
            'id': player_id,
            'name': player_name,
            'xp': 0,
            'history' = []
        }
        self.xp.insert_one(ret)
        return ret

    async def get_player(self, ctx):
        player_id = hash(ctx.message.author)
        res = self.xp.find_one(
            {
                'id': player_id
            }
        )
        if not res:
            res = await self.create_xp(ctx)
        return res

    @commands.has_role("GameMaster")
    @commands.command()
    async def givexp(self, ctx, points):
        res = await self.get_player(ctx)
        self.xp.update_one(
            {
                'id': res['id']
            },
            {
                'xp': res['xp'] + points
            }
        )
        await ctx.send("{0}'s XP is set to {1}.".format(res['name'], points))

    @commands.has_role("GameMaster")
    @commands.command()
    async def setxp(self, ctx, points):
        res = await self.get_player(ctx)
        self.xp.update_one(
            {
                'id': res['id']
            },
            {
                'xp': points
            }
        )
        await ctx.send("{0}'s XP is set to {1}.".format(res['name'], points))

    @commands.command()
    async def xp(self, ctx):
        res = await self.get_player(ctx)
        try:
            msg = await ctx.send('You have {} xp.'.format(res['xp']))  
        except Exception as e:
            await ctx.send("I has the xp dumbz. :P")
            raise e