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
        logger.debug('Connecting to Mongo...')
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
            res = await self.create_xp(message=message)
        
        player_hist = res['history']
        player_hist.append(
            {
                'date': dt.now(),
                'message': message.content
            }
        )

        self.xp.update_one(
            {
                'id': player_id
            },
            {
                '$set': {'history': player_hist}
            }
        )

    async def create_xp(self, ctx=None, message=None):
        if not message:
            message = ctx.message
        player_id = hash(message.author)
        player_name = str(message.author)
        ret = {
            'id': player_id,
            'name': player_name,
            'xp': 0,
            'history': []
        }
        self.xp.insert_one(ret)
        return ret

    async def get_player_by_ctx(self, ctx):
        player_id = hash(ctx.message.author)
        res = self.xp.find_one(
            {
                'id': player_id
            }
        )
        if not res:
            res = await self.create_xp(ctx=ctx)
        return res

    async def get_player_by_id(self, ctx):
        player_id = hash(ctx.message.author)
        res = self.xp.find_one(
            {
                'id': player_id
            }
        )
        if not res:
            res = await self.create_xp(ctx=ctx)
        return res

    @commands.has_role("GameMaster")
    @commands.command(pass_context=True)
    async def givexp(self, ctx, *, name="", points: int = 0):
        if name:
            try:
                user = ctx.message.mentions[0]
            except:
                user = ctx.guild.get_member_named(name)
            if not user:
                user = ctx.guild.get_member(int(name))
            if not user:
                await ctx.send('Could not find user.')
                return
        else:
            user = ctx.message.author
        res = await self.get_player_by_id(user)
        self.xp.update_one(
            {
                'id': res['id']
            },
            {'$set': {
                'xp': res['xp'] + points
            }}
        )
        await ctx.send("{0}'s XP is increased by {1}.".format(res['name'], points))

    @commands.has_role("GameMaster")
    @commands.command(aliases=['set_xp'],pass_context=True)
    async def setxp(self, ctx, *, name="", points: int = 0):
        if name:
            try:
                user = ctx.message.mentions[0]
            except:
                user = ctx.guild.get_member_named(name)
            if not user:
                user = ctx.guild.get_member(int(name))
            if not user:
                await ctx.send('Could not find user.')
                return
        else:
            user = ctx.message.author
        res = await self.get_player_by_id(user)
        self.xp.update_one(
            {
                'id': res['id']
            },
            {'$set': {
                'xp': points
            }}
        )
        await ctx.send("{0}'s XP is set to {1}.".format(res['name'], points))

    @commands.command(aliases=['experience'],pass_context=True)
    async def xp(self, ctx):
        if name:
            try:
                user = ctx.message.mentions[0]
            except:
                user = ctx.guild.get_member_named(name)
            if not user:
                user = ctx.guild.get_member(int(name))
            if not user:
                await ctx.send('Could not find user.')
                return
        else:
            user = ctx.message.author        
        logger.debug('Calling XP')
        res = await self.get_player_by_idx(user)
        msg = await ctx.send('You have {} xp.'.format(res['xp']))  

    @commands.command(aliases=['test'],pass_context=True)
    async def xptest(self, ctx):
        logger.debug('Calling XPtest')
        msg = await ctx.send('You have 10000000 xp.')  