import os
import sys
from zlib import crc32

import sqlalchemy.exc
from PIL import Image, ImageDraw, ImageFont
from nextcord import SlashOption, Interaction, slash_command, Client, User, File, Embed
from nextcord.ext import commands

from sqlalchemy import Column, Integer, Text, Numeric
from sqlalchemy.ext.declarative import declarative_base

from main import session

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

DeclarativeBase = declarative_base()


class TableAchievements(DeclarativeBase):
    __tablename__ = 'achievements'

    id = Column(Integer, primary_key=True)
    name = Column('name', Text)
    user = Column('user', Numeric)
    guild = Column('guild', Numeric)


def generate_img(text: str) -> str:
    """
    Checking image content with crc, and generating new image if nothing was founded.

    Return -> crc hash: (int) of image text
    """

    filenames = next(os.walk('images/unlocked'), (None, None, []))[2]
    crc = crc32(text.encode('utf-8'))

    if f"{crc}.png" not in filenames:
        img = Image.open("images/achievement.png")

        font_size = 24
        max_length = 370

        font = ImageFont.truetype("fonts/Bhanschrift.otf", size=font_size)
        font_length = font.getlength(text)
        while font_length > max_length:
            font_size -= 1
            font = ImageFont.truetype("fonts/Bhanschrift.otf", size=font_size)
            font_length = font.getlength(text)

        draw = ImageDraw.Draw(img)
        draw.text(
            (138, 62),
            text,
            font=font,
            fill='#e1cdb9',
        )

        img.save(f'images/unlocked/{crc}.png')

    return f"{crc}"


class Achievements(commands.Cog):

    def __init__(self, client):
        self.client: Client = client
        print("<7>Initialization Achievements.")

    @slash_command(name="achievement")
    async def achievement(self, interaction: Interaction):
        pass

    @achievement.subcommand(name="add", description="Выдать достижение пользователю")
    async def achievement_add(self,
                              interaction: Interaction,
                              user: User = SlashOption("пользователь"),
                              text: str = SlashOption("достижение")
                              ):
        text: str = "%s%s" % (text[0].upper(), text[1:])  # Uppercase first symbol

        # Check on member is at guild
        if user not in interaction.guild.members:
            await interaction.response.send_message("Пользователь не найден!", ephemeral=True)
            return

        _session = session()

        # Check on duplicating of achievement
        query = _session.query(TableAchievements).filter(
            TableAchievements.guild == interaction.guild_id,
            TableAchievements.user == user.id
        ).all()
        for achievement in query:
            if achievement.name == text:
                await interaction.response.send_message(
                    f"У {user.mention} уже есть достижение `{text}`",
                    ephemeral=True
                )
                return

        # Issuing achievement to user
        entry = TableAchievements(name=text, user=user.id, guild=interaction.guild_id)
        try:
            _session.add(entry)
        except sqlalchemy.exc.SQLAlchemyError:
            await interaction.response.send_message("Something goes wrong...", ephemeral=True)
            return
        finally:
            _session.commit()

        img_hash = generate_img(text)  # Generating achievement image
        await interaction.response.send_message(
            f"{user.mention} разблокировал достижение!",
            file=File(f'images/unlocked/{img_hash}.png')
        )

    @achievement.subcommand(name="remove", description="Лишить пользователя достижения")
    async def achievement_remove(self,
                                 interaction: Interaction,
                                 user: User = SlashOption("пользователь"),
                                 text: str = SlashOption("достижение")
                                 ):
        # Check on member is at guild
        if user not in interaction.guild.members:
            await interaction.response.send_message("Пользователь не найден!", ephemeral=True)
            return

        _session = session()

        # Check on existing of achievement
        query = _session.query(TableAchievements).filter(
            TableAchievements.guild == interaction.guild_id,
            TableAchievements.user == user.id,
            TableAchievements.name == text
        )
        if len(query.all()) > 0:
            # Delete achievement
            query.delete()
            _session.commit()
            await interaction.response.send_message(f"{user.mention} лишен достижения `{text}`!")
        else:
            await interaction.response.send_message(
                f"У {user.mention} нету достижения `{text}`",
                ephemeral=True
            )

    @slash_command(name="rewards", description="Посмотреть список достижений пользователя")
    async def achievement_list(self,
                               interaction: Interaction,
                               user: User = SlashOption(name="пользователь")
                               ):
        _session = session()

        # Check user's achievements
        query = _session.query(TableAchievements).filter(
            TableAchievements.guild == interaction.guild_id,
            TableAchievements.user == user.id
        ).all()
        if len(query) > 0:
            embed = Embed(title=f"Достижения {user.display_name} ({len(query)})", color=0x97cc01)
            i = 1
            for achievement in query:
                embed.add_field(value=f"`{achievement.name}`", name=f"Достижение #{i}")
                i += 1

            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message(
                embed=Embed(title=f"У {user.display_name} нету достижений :(", color=0x97cc01)
            )


def setup(client):
    client.add_cog(Achievements(client))
