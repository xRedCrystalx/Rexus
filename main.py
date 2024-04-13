import discord, aiohttp, os, sys, glob
sys.dont_write_bytecode = True
from discord.ext import commands
import src.connector as con


class MyBot(commands.AutoShardedBot):
    def __init__(self) -> None:
        super().__init__(command_prefix="-", intents=discord.Intents.all(), shard_count=2, help_command=None)
        self.shared: con.Shared = con.shared

        self.shared.path = os.path.dirname(os.path.realpath(__file__))
        self.c = self.shared.colors
        self.shared.bot = self

    async def setup_hook(self) -> None:
        self.shared.system_load()
        self.shared.plugin_load()
        self.session = self.shared.session = aiohttp.ClientSession()

        print(rf"""{self.c.Yellow}
    _   __      ____  _            
   / | / /___  / __ \(_)___  ____ _
  /  |/ / __ \/ /_/ / / __ \/ __ `/
 / /|  / /_/ / ____/ / / / / /_/ / 
/_/ |_/\____/_/   /_/_/ /_/\__, /  
                          /____/   
{self.c.R}Loading... Please wait. 
{self.c.Gray}---------------------------------------------------{self.c.R}""")
        print(f"Found {self.c.Magenta}{len(os.listdir(f"{self.shared.path}/databases/servers"))}{self.c.R} server databases.")
        print(f"Found {self.c.Magenta}{len(os.listdir(f"{self.shared.path}/databases/users"))}{self.c.R} user databases.")

        print(f"{self.c.Gray}---------------------------------------------------\n{self.c.R}[{self.c.Green}+{self.c.R}]    Loading Global Extensions...")

        cogPaths: tuple[str, ...] = ("src/core/listeners", "src/core/commands")
        for path in cogPaths:
            print(f"{self.c.Green}+{self.c.R} Loading {path}..")
            counter = 0
            for cog in (cogList := glob.glob(f"{path}/**/*.py" if self.shared.OS == "Windows" else f"*/{path}/**/*.py", recursive=True)):
                try:
                    await self.load_extension(cog.replace("\\", ".").replace("/", ".").removesuffix(".py"))
                    counter += 1
                except Exception as error:
                    print(f"{self.c.Red}Failed to load {cog}: {type(error).__name__}; {error}{self.c.R}")
            
            print(f"{self.c.Cyan}i{self.c.R} Successfully loaded {self.c.Cyan}{counter}/{len(cogList)}{self.c.R} extensions.")
        
        print(f"{self.c.Gray}---------------------------------------------------\n{self.c.R}[{self.c.Green}+{self.c.R}]    Syncing...")
        if not (synced := await self.tree.sync()):
            print(f"{self.c.Red}Syncing failed.{self.c.R}")
        else:
            print(f"{self.c.Green}Synced {len(synced)} commands globally{self.c.R}")
                
        print(f"{self.c.Gray}---------------------------------------------------{self.c.R}\nConsole:")

    async def close(self) -> None:
        await super().close()
        await self.session.close()

    async def on_ready(self) -> None:
        print(f"{self.c.Magenta}{self.user} has connected to Discord!{self.c.R}")
        await self.change_presence(status=discord.Status.online, activity=discord.Activity(type=discord.ActivityType.playing, name="V3 out!"))

if __name__ == "__main__":
    MyBot().run("SECRET-TOKEN", reconnect=True, log_handler=None)
