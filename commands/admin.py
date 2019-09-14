import discord
import asyncio
import random
from discord.ext import commands
from discord.utils import get

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_role("Vanir")
    async def hellfire(self, ctx, member: discord.Member):
        if member.id == 189761449013280768:
            await ctx.send("No.")
            return

        role = get(member.guild.roles, name='Eljudne')

        print(role)

        await member.add_roles(role)

