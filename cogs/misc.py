import os
import sys

import nextcord.ext.commands
# from nextcord import Member, VoiceState, VoiceChannel, PermissionOverwrite
from nextcord.ext import commands

# from main import session

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))


class Misc(commands.Cog):
    def __init__(self, client):
        self.client = client
        print("<7>Initialization MiscFunctions.")

    @commands.command()
    async def emoji(self, ctx: nextcord.ext.commands.Context, emoji: str):
        await ctx.reply(f'`{emoji}`')

    @emoji.error
    async def emoji_error(self, ctx: nextcord.ext.commands.Context):
        await ctx.message.add_reaction('❓')


def setup(client):
    client.add_cog(Misc(client))
