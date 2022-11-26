import os
import sys

from nextcord import PartialEmoji, Member, Client, RawReactionActionEvent
from nextcord.ext import commands

from sqlalchemy import Column, Text, Numeric, Integer
from sqlalchemy.ext.declarative import declarative_base

from main import session

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

DeclarativeBase = declarative_base()


class TableReactionRoles(DeclarativeBase):
    __tablename__ = "reaction_roles"

    id = Column(Integer, primary_key=True)
    role_id = Column('role_id', Numeric)
    reaction = Column('reaction', Text)
    message = Column('message', Numeric)
    channel = Column('channel', Numeric)
    guild = Column('guild', Numeric)


class RoleManager(commands.Cog):
    def __init__(self, client):
        self.client: Client = client
        print("<7>Initialization RoleManager.")

    @staticmethod
    async def manage_role(
            member: Member,
            emoji: PartialEmoji,
            message_id: int,
            guild_id: int,
            channel_id: int,
            state: bool
    ):
        _session = session()

        query = _session.query(TableReactionRoles).filter(
            TableReactionRoles.guild == guild_id,
            TableReactionRoles.channel == channel_id,
            TableReactionRoles.message == message_id
        ).all()

        for entry in query:
            if str(emoji) == entry.reaction:
                role = member.guild.get_role(entry.role_id)
                if state:
                    await member.add_roles(role)
                else:
                    await member.remove_roles(role)

    @commands.Cog.listener()
    async def on_raw_reaction_add(
            self,
            payload: RawReactionActionEvent
    ):
        if payload.member.bot:
            return
        await self.manage_role(
            payload.member,
            payload.emoji,
            payload.message_id,
            payload.guild_id,
            payload.channel_id,
            True
        )

    @commands.Cog.listener()
    async def on_raw_reaction_remove(
            self,
            payload: RawReactionActionEvent
    ):
        member = self.client.get_guild(payload.guild_id).get_member(payload.user_id)
        if member.bot:
            return
        await self.manage_role(
            member,
            payload.emoji,
            payload.message_id,
            payload.guild_id,
            payload.channel_id,
            False
        )


def setup(client):
    client.add_cog(RoleManager(client))
