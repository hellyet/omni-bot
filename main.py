import nextcord
from nextcord.ext import commands
import yaml
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine.url import URL

with open('config.yaml', 'r') as db_file:
    cfg = yaml.load(db_file, Loader=yaml.FullLoader)

# import sys, os
# sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

# journalctl #
# 1 - red
# 4 - yellow
# 5 - white bold
# 7 - grey


engine = create_engine(URL.create(**cfg['database']), client_encoding='utf-8')
session = sessionmaker(bind=engine)


class MainBot(commands.Bot):
    default_guild_ids = []

    def __init__(self, command_prefix, **options):
        super().__init__(command_prefix, **options)

    async def on_ready(self):
        print("<4>Loading guilds...")
        for guild in self.guilds:
            self.default_guild_ids.append(guild.id)
        print(f'<1>Logged as {self.user} on {len(self.default_guild_ids)} guild{"" if len(self.default_guild_ids) == 1 else "s"}')

    async def on_guild_join(self, guild: nextcord.Guild):
        print(f"<1>Joined to guild {guild.name}")
        self.default_guild_ids.append(guild.id)

# --------------------------- #
# LOADING CLIENT AND COGS #
# --------------------------- #


client = MainBot(
    command_prefix=cfg['prefix'],
    intents=nextcord.Intents.all()
)


@client.command()
async def cogs(ctx: commands.Context, cmd: str, name: str):
    if ctx.author.id == 365852454866255872:
        if cmd == "reload":
            client.reload_extension(f"cogs.{name}")
        elif cmd == "unload":
            client.unload_extension(f"cogs.{name}")
        elif cmd == "load":
            client.load_extension(f"cogs.{name}")
        else:
            await ctx.message.add_reaction('❓')
            return
        await ctx.message.add_reaction('✅')


@cogs.error
async def reload_error(ctx: commands.Context, error):
    if ctx.author.id == 365852454866255872:
        await ctx.send('```{}```'.format(error))

if __name__ == "__main__":
    print("<4>Loading cogs...")
    client.load_extension('cogs.misc')
    client.load_extension('cogs.achievements')
    client.load_extension('cogs.voice')
    client.load_extension('cogs.roles')
    client.load_extension('cogs.config')
    client.run(cfg['token'])
