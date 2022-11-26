import os
import sys

from nextcord import Member, VoiceState, VoiceChannel, PermissionOverwrite
from nextcord.ext import commands

from sqlalchemy import Column, Integer, Numeric
from sqlalchemy.ext.declarative import declarative_base

from main import session

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

DeclarativeBase = declarative_base()


class TableVoiceRooms(DeclarativeBase):
    __tablename__ = 'voice_rooms'

    id = Column(Integer, primary_key=True)
    guild = Column('guild', Numeric)
    channel = Column('channel', Numeric)
    category = Column('category', Numeric)


class VoiceRooms(commands.Cog):
    def __init__(self, client):
        self.client = client
        print("<7>Initialization VoiceRooms.")

    @commands.Cog.listener()
    async def on_voice_state_update(
            self,
            member: Member,
            before: VoiceState,
            after: VoiceState
    ):
        _channels, _categories = [], []
        _session = session()

        query = _session.query(TableVoiceRooms).filter(
            TableVoiceRooms.guild == (before.channel.guild.id if not after.channel else after.channel.guild.id)
        ).all()

        for entry in query:
            _channels.append(entry.channel)
            _categories.append(entry.category)

        if after.channel and after.channel.category_id in _categories:
            if after.channel.id in _channels:
                perms = PermissionOverwrite(
                    move_members=True,
                    mute_members=True,
                    deafen_members=True,
                    manage_channels=True
                )

                channel: VoiceChannel = await after.channel.category.create_voice_channel(
                    name=f"🔈-{member.display_name}",
                    overwrites={member: perms}
                )
                await member.move_to(channel)
        if before.channel and \
                before.channel.category_id in _categories and \
                before.channel.id not in _channels and \
                len(before.channel.members) == 0:
            await before.channel.delete()


def setup(client):
    client.add_cog(VoiceRooms(client))
