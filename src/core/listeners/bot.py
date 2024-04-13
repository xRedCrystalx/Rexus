import discord, json, sys, schedule
sys.dont_write_bytecode = True
from discord.ext import commands
import src.connector as con

class BotListeners(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.shared: con.Shared = con.shared
        self.bot: commands.Bot = bot
        self.c: con.Colors.C | con.Colors.CNone = self.shared.colors

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild) -> None:
        self.shared.logger.log(f"Successfully joined {self.c.Cyan}{guild.name} {self.c.R}({guild.id})! {self.c.DBlue}Info{self.c.R}: Mnum: {guild.member_count}, Owner: {guild.owner.name} ({guild.owner_id})")
        
        await self.bot.tree.sync(guild = discord.Object(id=guild.id))
        channel: discord.TextChannel = guild.system_channel

        CopyDB: dict = json.load(open(f"{self.shared.path}/src/system/CopyDB.json", "r"))
        file: str = f"{self.shared.path}/databases/servers/{guild.id}.json"

        try:
            with open(file, "r"):
                self.shared.logger.log(f"Found {self.c.Yellow}database for {self.c.Cyan}{guild.name}.")

        except FileNotFoundError as error:
            try:
                with open(file, "w+") as file3:
                    json.dump(CopyDB, file3, indent=4)

            except Exception as error:
                id: str = self.shared._create_id()
                await channel.send(f"Failed to create database. Please contact @xRedCrystalx. Error ID: `{id}`")
                self.shared.logger.log(f"Failed to {self.c.Red}create database file{self.c.R} for server {self.c.Cyan}{guild.name} ({guild.id}){self.c.R}. {self.c.DBlue}ID{self.c.R}: {self.c.Red}{id} Error: {type(error).__name__}: {error}{self.c.R}", "ERROR")

            try:  
                with open(file, "r") as file4:
                    json.load(file4)
                    self.shared.logger.log(f"Successfully {self.c.Green}saved and read Database{self.c.R} for server {self.c.Cyan}{guild.name} ({guild.id}){self.c.R}.")

            except Exception as error:
                id: str = self.shared._create_id()
                await channel.send(f"Failed to create database. Please contact @xRedCrystalx. Error ID: {id}")
                self.shared.logger.log(f"Failed to {self.c.Red}read database file{self.c.R} for server {self.c.Cyan}{guild.name} ({guild.id}){self.c.R}. {self.c.DBlue}ID{self.c.R}: {self.c.Red}{id} Error: {type(error).__name__}: {error}{self.c.R}", "ERROR")

        except Exception as error:
            id: str = self.shared._create_id()
            await channel.send(f"Failed to create database. Please contact @xRedCrystalx. Error ID: {id}")
            self.shared.logger.log(f"Global database file exception{self.c.R} for server {self.c.Cyan}{guild.name} ({guild.id}){self.c.R} has occured. {self.c.DBlue}ID{self.c.R}: {self.c.Red}{id} Error: {type(error).__name__}: {error}{self.c.R}", "ERROR")

        await channel.send("Thank you for inviting me to your server! To start with my configuration, execute `/help` command!")

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(BotListeners(bot))
