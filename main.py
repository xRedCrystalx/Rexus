import discord, aiohttp, os, sys, glob, logging, pprint
sys.dont_write_bytecode = True
from discord.ext import commands
from src.connector import shared

from xRedUtilsAsync.errors import full_traceback
from xRedUtilsAsync.colors import (
    Foreground16 as FG,
    Style as ST
)

class MyBot(commands.AutoShardedBot):
    def __init__(self) -> None:
        super().__init__(command_prefix="-", intents=discord.Intents.all(), shard_count=2, help_command=None, max_messages=100)

        shared.path = os.path.dirname(os.path.realpath(__file__))
        shared.bot = self

    async def setup_hook(self) -> None:
        shared.system_load()
        self.session = shared.session = aiohttp.ClientSession()

        print(rf"""{FG.YELLOW}
    _   __      ____  _
   / | / /___  / __ \(_)___  ____ _
  /  |/ / __ \/ /_/ / / __ \/ __ `/
 / /|  / /_/ / ____/ / / / / /_/ / 
/_/ |_/\____/_/   /_/_/ /_/\__, /  
                          /____/   
{ST.RESET}Loading... Please wait. 
{FG.BLACK}──────────────────────────────────────────────────{ST.RESET}""")
        print(f"Found {FG.MAGENTA}{len(os.listdir(f"{shared.path}/databases/guilds"))}{ST.RESET} server databases.")
        print(f"Found {FG.MAGENTA}{len(os.listdir(f"{shared.path}/databases/users"))}{ST.RESET} user databases.")
        print(f"{FG.BLACK}──────────────────────────────────────────────────{ST.RESET}")

        cogPaths: tuple[str, ...] = ("src/core/listeners", "src/core/commands", "src/core/plugins")
        for path in cogPaths:
            print(f"{FG.GREEN}+{ST.RESET} Loading {path}..")
            counter = 0
            for cog in (cogList := [*glob.glob(f"{path}/*.py"), *glob.glob(f"{path}/*/*.py")]):
                try:
                    await self.load_extension(cog.replace("\\", ".").replace("/", ".").removesuffix(".py"))
                    counter += 1
                except Exception:
                    print(f"{FG.RED}Failed to load {cog}:\n{await full_traceback()}{ST.RESET}")

            print(f"{FG.CYAN}i{ST.RESET} Successfully loaded {FG.CYAN}{counter}/{len(cogList)}{ST.RESET} extensions.")
        
        print(f"{FG.BLACK}──────────────────────────────────────────────────{ST.RESET}")
        if not (synced := await self.tree.sync()):
            print(f"{FG.RED}Syncing failed.{ST.RESET}")
        else:
            print(f"{FG.GREEN}Synced {len(synced)} commands globally{ST.RESET}")

        if not (testing_guild_sync := await self.tree.sync(guild=discord.Object(id=1230040815116484678))):
            print(f"{FG.RED}Syncing to testing guild failed.{ST.RESET}")
        else:
            print(f"{FG.GREEN}Synced {len(testing_guild_sync)} commands to testing guild.{ST.RESET}")

        print(f"{FG.BLACK}──────────────────────────────────────────────────{ST.RESET}\nConsole:")

    async def close(self) -> None:
        await super().close()
        await self.session.close()

    async def on_command_error(self, ctx: commands.Context, error: commands.CommandError) -> None:
        if not isinstance(error, commands.CommandNotFound):
            await super().on_command_error(ctx, error)

    async def on_ready(self) -> None:
        print(f"{FG.MAGENTA}{self.user} has connected to Discord!{ST.RESET}")
        await self.change_presence(status=discord.Status.online, activity=discord.Activity(type=discord.ActivityType.playing, name="Hi there :)"))

if __name__ == "__main__":
    MyBot().run("TOKEN", reconnect=True, log_level=logging.INFO)
