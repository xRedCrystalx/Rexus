import discord, aiohttp, os, sys, glob
sys.dont_write_bytecode = True
from discord.ext import commands
from src.connector import shared

from xRedUtils.errors import full_traceback
from xRedUtils.colors import (
    Foreground255 as FG,
    Style as ST
)

class Rexus(commands.AutoShardedBot):
    def __init__(self) -> None:
        shared.path = os.path.dirname(os.path.realpath(__file__))
        shared.bot =  self

        super().__init__(command_prefix="-", intents=discord.Intents.all(), shard_count=2, help_command=None, max_messages=100)

    async def system_load(self) -> bool:
        from src.system.module_manager import ModuleManager
        shared.module_manager = ModuleManager()

        for sys_module in glob.glob(f"src/system/*.py"):
            if not sys_module.endswith("module_manager"):
                await shared.module_manager.load(sys_module.replace("\\", ".").replace("/", ".").removesuffix(".py"))

        return all((shared.module_manager, shared.logger, shared.db_read, shared.db_write, shared.queue)) and all((shared.loop, shared.bot, shared.session, shared.path))

    async def setup_hook(self) -> None:
        shared.session = self.session = aiohttp.ClientSession()
        print(rf"""{FG.RED}
____ ____ _  _ _  _ ____ 
|__/ |___  \/  |  | [__  
|  \ |___ _/\_ |__| ___]

{ST.RESET}Loading... Please wait. 
{FG.GREY}──────────────────────────────────────────{ST.RESET}""")
        shared.loop = self.loop
        
        if not await self.system_load():
            print(f"{FG.RED}Error: Failed to initialize critical systems.{ST.RESET}")
            return await self.close()

        for path in ("src/core/helpers", "src/core/listeners", "src/core/plugins", "src/core/commands"):
            print(f"{FG.GREEN}+{ST.RESET} Loading {path}..")
            counter = 0
            for cog in (cogList := glob.glob(f"{path}/**/*.py", recursive=True)):
                try:
                    await shared.module_manager.load(cog.replace("\\", ".").replace("/", ".").removesuffix(".py"))
                    counter += 1
                except Exception:
                    print(f"{FG.RED}Failed to load {cog}:\n{full_traceback()}{ST.RESET}")

            print(f"{FG.CYAN}i{ST.RESET} Successfully loaded {FG.CYAN}{counter}/{len(cogList)}{ST.RESET} extensions.")

        print(f"{FG.GREY}──────────────────────────────────────────{ST.RESET}\nConsole:")

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
    Rexus().run("TOKEN", reconnect=True, log_level=20)
