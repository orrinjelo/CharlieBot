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
from pprint import pformat

logger = logging.getLogger('discord')

class Roleplay(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.session = aiohttp.ClientSession(loop=self.bot.loop, headers={"User-Agent": "AppuSelfBot"})
        self.mongo_client = MongoClient()
        self.rp_db = self.mongo_client['rp']
        self.xp = self.rp_db.xp
        self.characters = self.rp_db.characters

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
        player_xp = res['xp']
        now = dt.now()
        date = str(now.year*10000 + now.month*100 + now.day)
        if date in player_hist:
            player_hist[date] += 1
        else:
            player_hist[date] = 1
            player_xp += 1

        self.xp.update_one(
            {
                'id': player_id
            },
            {
                '$set': {
                    'history': player_hist,
                    'xp': player_xp
                }
            }
        )

    async def create_xp(self, ctx=None, message=None, member=None):
        if not message:
            message = ctx.message
        if not member:
            member = message.author
        player_id = hash(member)
        player_name = str(member)
        res = self.xp.find_one(
            {
                'name': player_name
            }
        )
        if res:
            channel = self.bot.get_channel(BOT_DEBUG_CHANNEL)
            await channel.send('Error: {}({}) already exists in database'.format(player_name, player_id))
            return res
        ret = {
            'id': player_id,
            'name': player_name,
            'xp': 0,
            'history': {}
        }
        self.xp.insert_one(ret)
        return ret

    async def create_character(self, ctx, name):
        message = ctx.message
        member = message.author
        player_id = hash(member)
        player_name = str(member)
        char_name = name
        res = self.characters.find_one(
            {
                'name': player_name
            }
        )
        if res:
            channel = self.bot.get_channel(BOT_DEBUG_CHANNEL)
            await channel.send('Error: {}({}) already exists in database'.format(player_name, player_id))
            return res
        ret = {
            'id': player_id,
            'name': player_name,
            'wounds': 0,
            'strain': 0,
            'soak': 0,
            'defense': {
                'ranged': 0,
                'melee': 0
            },
            'character': {
                'name': char_name,
                'career': '',
                'specializations': [],
                'species': '',
                'base_skills': {
                    'INT': 0,
                    'BRA': 0,
                    'PRE': 0,
                    'WIL': 0,
                    'AGI': 0,
                    'CUN': 0
                },
                'ranks': {
                    'astrogation': 0,
                    'athletics': 0,
                    'brawl': 0,
                    'charm': 0,
                    'coercion': 0,
                    'computers': 0,
                    'cool': 0,
                    'coordination': 0,
                    'cybernetics': 0,
                    'deception': 0,
                    'discipline': 0,
                    'education': 0,
                    'gunnery': 0,
                    'knowledge core worlds': 0,
                    'knowledge education': 0,
                    'knowledge lore': 0,
                    'knowledge outer rim': 0,
                    'knowledge underworld': 0,
                    'knowledge warfare': 0,
                    'knowledge xenology': 0,
                    'leadership': 0,
                    'lightsaber': 0,
                    'mechanics': 0,
                    'medicine': 0,
                    'melee': 0,
                    'negotiation': 0,
                    'perception': 0,
                    'piloting planetary': 0,
                    'piloting space': 0,
                    'ranged heavy': 0,
                    'ranged light': 0,
                    'resilience': 0,
                    'skullduggery': 0,
                    'stealth': 0,
                    'streetwise': 0,
                    'survival': 0,
                    'vigilance': 0,
                },
                'skill_characteristic': {
                    'INT': [
                        'astrogation',
                        'computers',
                        'knowledge core worlds',
                        'knowledge education',
                        'knowledge lore',
                        'knowledge outer rim',
                        'knowledge underworld',
                        'knowledge warfare',
                        'knowledge xenology',
                        'cybernetics',
                        'mechanics',
                        'medicine'
                    ],
                    'BRA': [
                        'athletics',
                        'brawl',
                        'lightsaber',
                        'melee',
                        'resilience'
                    ],
                    'PRE': [
                        'charm',
                        'cool',
                        'leadership',
                        'negotiation'
                    ],
                    'WIL': [
                        'coercion',
                        'discipline',
                        'vigilance'
                    ],
                    'AGI': [
                        'coordination',
                        'gunnery',
                        'piloting planetary',
                        'piloting space',
                        'ranged heavy',
                        'ranged light',
                        'stealth'
                    ],
                    'CUN': [
                        'deception',
                        'perception',
                        'skullduggery',
                        'streetwise',
                        'survival'
                    ]
                },
                'duty': {
                    'type': '',
                    'points': ''
                },
                'critical_injuries': [],
                'weapons': [],
                'equipment': [],
                'talents': [],
                'credits': [],
                'max_encumberance': 0,
                'total_xp': 0,
                'available_xp': 0,
                'history_brief': '',
                'appearance_brief': '',
                'thumbnail': ''
            }
        }
        self.characters.insert_one(ret)
        return ret

    async def report_characters_pid(self, ctx, player_id):
        char = self.characters.find_one(
            {
                'id': player_id
            }
        )
        # # Thanks to IgneelDxD for help on this
        # if str(user.avatar_url)[54:].startswith('a_'):
        #     avi = 'https://images.discordapp.net/avatars/' + str(user.avatar_url)[35:-10]
        # else:
        #     avi = user.avatar_url        
        if char:
            if embed_perms(ctx.message):
                em = discord.Embed(colour=0x708DD0)
                em.add_field(name='Player', value=char['name'], inline=True)
                em.add_field(name='Character', value=char['character']['name'], inline=True)
                em.add_field(name='Characteristics', value=' '.join(['**{0}**:{1}'.format(s, char['character']['base_skills'][s]) for s in char['character']['base_skills']]), inline=True)
                em.add_field(name='Career', value=char['character']['career'], inline=True)
                em.add_field(name='Species', value=char['character']['species'], inline=True)
                em.add_field(name='Specializations', value=''+', '.join(char['character']['specializations']), inline=True)
                em.add_field(name='Appearance', value=char['character']['appearance_brief'], inline=True)
                try:
                    em.set_thumbnail(url=char['character']['thumbnail'])
                except:
                    pass
                await ctx.send(embed=em)
            else:
                msg = 'Unimplemented'
                await ctx.send(msg)        
        else:
            await ctx.send('Character not found.')

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

    async def get_player_by_id(self, ctx, player_id):
        res = self.xp.find_one(
            {
                'id': hash(player_id)
            }
        )
        if not res:
            res = await self.create_xp(ctx=ctx)
        return res

    async def get_player_by_member(self, ctx, member):
        res = self.xp.find_one(
            {
                'id': hash(member)
            }
        )
        if not res:
            res = await self.create_xp(ctx=ctx, member=member)
        return res

    @commands.command(pass_context=True, aliases=['new_character'])
    async def newchar(self, ctx, name):
        await self.create_character(ctx, name)
        await ctx.send('Character created.')

    @commands.command(pass_context=True, aliases=['character'])
    async def char(self, ctx):
        message = ctx.message
        member = message.author
        player_id = hash(member)
        await self.report_characters_pid(ctx, player_id)

    @commands.command(pass_context=True, aliases=['listxpraw'])
    async def xplistraw(self, ctx):
        res = self.xp.find()
        for entry in res:
            await ctx.send(pformat(entry))

    @commands.command(pass_context=True, aliases=['listxp'])
    async def xplist(self, ctx):
        res = self.xp.find()
        for entry in res:
            user = ctx.guild.get_member_named(entry['name'])
            try:
                if user.nick:
                    username = user.nick
                else:
                    username = user.name
            except:
                username = user.name
            await ctx.send('{} has {} XP.'.format(username, entry['xp']))

    @commands.command(pass_context=True)
    @commands.has_role("Vanir")
    async def find_one(self, ctx, query: str):
        res = self.xp.find_one(
            eval(query)
        )
        await ctx.send(pformat(res))

    @commands.command(pass_context=True)
    @commands.has_role("Vanir")
    async def update_one(self, ctx, query: str, request: str):
        res = self.xp.update_one(
            eval(query),
            eval(request)
        )
        await ctx.send(pformat(res))

    @commands.has_role("GameMaster")
    @commands.command(pass_context=True)
    async def givexp(self, ctx, points: int, *, name: discord.Member=None):
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
        res = await self.get_player_by_member(ctx, user)
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
    async def setxp(self, ctx, points: int, *, name: discord.Member=None):
        # await ctx.send("{},{}".format(points, name))
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
        res = await self.get_player_by_member(ctx, user)
        # await ctx.send("{},{},{},{}".format(user,hash(user),res,hash(ctx.message.author)))
        self.xp.update_one(
            {
                'id': res['id']
            },
            {'$set': {
                'xp': points
            }}
        )
        await ctx.send("{0}'s XP is set to {1}.".format(str(user), points))

    @commands.command(aliases=['experience'],pass_context=True)
    async def xp(self, ctx, name: discord.Member=None):
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
        res = await self.get_player_by_member(ctx,user)
        msg = await ctx.send('{} has {} xp.'.format(str(user), res['xp']))  

    @commands.command(aliases=['test'],pass_context=True)
    async def xptest(self, ctx):
        logger.debug('Calling XPtest')
        msg = await ctx.send('You have 10000000 xp.')  