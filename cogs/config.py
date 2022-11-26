import os
import sys

from nextcord import SlashOption, Interaction, slash_command, Client, VoiceChannel, \
    Message, Role, NotFound, Locale
from nextcord.ext import commands

# from sqlalchemy import Column, Integer, Text, Numeric
# from sqlalchemy.ext.declarative import declarative_base

from main import session
from cogs.roles import TableReactionRoles

from cogs.voice import TableVoiceRooms

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))


class ConfigManager(commands.Cog):
    def __init__(self, client):
        self.client: Client = client
        print("<7>Initialization ConfigManager.")

    @slash_command(name="config")
    async def config(self, interaction: Interaction):
        pass

    # Reaction Roles
    @config.subcommand(name="reactionroles")
    async def rr(self, interaction: Interaction):
        pass

    @rr.subcommand(name="add",
                   description_localizations={
                       Locale.en_US: locale["config"]["ReactionRoleAddDesc"]["en"],
                       Locale.ru: locale["config"]["ReactionRoleAddDesc"]["ru"]
                   })
    async def rr_add(
            self,
            interaction: Interaction,
            message_id=SlashOption(),
            emoji: str = SlashOption(),
            role: Role = SlashOption()
    ):
        _session = session()

        try:
            message: Message = await interaction.channel.fetch_message(message_id)
        except NotFound:
            await interaction.response.send_message(
                "Сообщение не найдено!\n"
                "Команду нужно использовать в канале, где находится сообщение.",
                ephemeral=True
                )
            return

        _session.add(TableReactionRoles(
            role_id=role.id,
            reaction=emoji,
            message=message_id,
            channel=interaction.channel_id,
            guild=interaction.guild_id
        ))
        _session.commit()
        await interaction.response.defer()
        await message.add_reaction(emoji)
        await interaction.followup.send("Done!", ephemeral=True)

    @rr.subcommand(name="remove", description="Отвязать выдачу роли по реакции от сообщения")
    async def rr_remove(
            self,
            interaction: Interaction,
            message_id=SlashOption(),
            emoji: str = SlashOption(),
    ):
        _session = session()

        try:
            message: Message = await interaction.channel.fetch_message(message_id)
        except NotFound:
            await interaction.response.send_message(
                "Сообщение не найдено!\n"
                "Команду нужно использовать в канале, где находится сообщение.",
                ephemeral=True
                )
            return

        _session.query(TableReactionRoles).filter(
            TableReactionRoles.guild == interaction.guild_id,
            TableReactionRoles.channel == interaction.channel_id,
            TableReactionRoles.message == message_id,
            TableReactionRoles.reaction == emoji
        ).delete()
        _session.commit()

        await interaction.response.defer()
        await message.remove_reaction(emoji, self.client.user)
        await interaction.followup.send("Done!", ephemeral=True)

    # Voice Rooms
    @config.subcommand(name="voice")
    async def voice(self, interaction: Interaction):
        pass

    @voice.subcommand(name="add", description="Назначить канал мастер-каналом категории")
    async def voice_add(
            self,
            interaction: Interaction,
            channel: VoiceChannel = SlashOption("мастер-канал")
    ):
        if channel.category_id is None:
            await interaction.response.send_message("Голосовой канал должен быть вложен в категорию.")
            return
        else:
            _session = session()

            query = _session.query(TableVoiceRooms).filter(
                TableVoiceRooms.guild == channel.guild.id,
                TableVoiceRooms.category == channel.category.id,
                TableVoiceRooms.channel == channel.id
            ).all()
            if len(query) > 0:
                await interaction.response.send_message(f"Ошибка! Канал {channel.mention} уже назначен мастер-каналом.")
            else:
                _session.add(TableVoiceRooms(
                    guild=channel.guild.id,
                    category=channel.category.id,
                    channel=channel.id
                ))
                _session.commit()
                await interaction.response.send_message(
                    f"Канал {channel.mention} назначен для мастер-каналом в категории `{channel.category.name}`.`"
                )

    @voice.subcommand(name="remove", description="Отключить мастер-канал категории.")
    async def voice_remove(
            self,
            interaction: Interaction,
            channel: VoiceChannel = SlashOption("мастер-канал")
    ):
        if channel.category_id is None:
            await interaction.response.send_message("Мастер-канал не вложен в категорию!")
            return

        _session = session()

        query = _session.query(TableVoiceRooms).filter(
            TableVoiceRooms.guild == channel.guild.id,
            TableVoiceRooms.category == channel.category.id,
            TableVoiceRooms.channel == channel.id
        )
        if len(query.all()) > 0:
            await interaction.response.send_message(f"{channel.mention} больше не является мастер-каналом!")
            query.delete()
            _session.commit()
        else:
            await interaction.response.send_message(f"Ошибка! {channel.mention} не назначен мастер-каналом категории.")


def setup(client):
    client.add_cog(ConfigManager(client))
