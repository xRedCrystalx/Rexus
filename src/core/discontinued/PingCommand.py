import discord, sys, traceback, typing
sys.dont_write_bytecode = True
from discord.ext import commands
from discord import app_commands
import src.connector as con


class PingCommand(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.shared: con.Shared = con.shared
        self.bot: commands.Bot = bot
        self.c: con.Colors.C | con.Colors.CNone = self.shared.colors

    @app_commands.command(name = "ping", description = "Ping!")
    async def ping(self, interaction: discord.Interaction, args: str = "/") -> None:
        BotData: dict =  self.shared.db.load_data()

        if interaction.user.id in BotData["owners"] and args != "/":
            functions: list[str] = args.split(".")
            cmds = CMDS(bot=self.bot, interaction=interaction)
            returned_data = None
            for function in functions:
                try:
                    split: list[str] = function.split('(')
                    method_name: str = split[0]
                    method_args: list[typing.Any] = [eval(x) for x in split[1][:-1].split(",")] if split[1] != ")" else []
                    method = getattr(cmds, method_name)
                    returned_data = method(returned_data=returned_data, *method_args)
                except Exception as error:
                    returned_data: str = f"```{traceback.format_exc()}```"
                    break
            await interaction.response.send_message(content=returned_data)
        else:
            await interaction.response.send_message(f"Pong! Running on {round(self.bot.latency * 1000)}ms")
            self.shared.logger.log(f"{self.c.Magenta}{interaction.user.name} ({interaction.user.id}){self.c.R} used {self.c.Yellow}/ping{self.c.R} slash command. {self.c.DBlue}Guild{self.c.R}: {interaction.guild.name}")

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(PingCommand(bot))


class CMDS:
    def __init__(self, bot: commands.Bot, interaction: discord.Interaction) -> None:
        self.bot: commands.Bot = bot
        self.interaction: discord.Interaction = interaction

    def load_guilds(self, returned_data: typing.Any, *args, **kwargs) -> str:
        guilds: str = "```"
        for guild in self.bot.guilds:
            guilds += f"{guild.name: <50}{guild.id}\n"
        return guilds+"```"

    def get_guild(self, id: int, returned_data: typing.Any, *args, **kwargs) -> discord.Guild:
        return self.bot.get_guild(id)

    def this_guild(self, returned_data: typing.Any, *args, **kwargs) -> discord.Guild:
        return self.interaction.guild

    def channel_structure(self, returned_data: discord.Guild, *args, **kwargs) -> str:
        string: str = "```"
        for category in returned_data.categories:
            string += f"﹀ {category.name}\n"
            for channel in category.channels:
                emoji: str = ""
                match channel.type:
                    case discord.ChannelType.voice:
                        emoji: str = "🔊"
                    case discord.ChannelType.stage_voice:
                        emoji: str = "📣"
                    case discord.ChannelType.forum:
                        emoji: str = "📁"
                    case discord.ChannelType.text:
                        emoji: str = "💬"
                string += f"{emoji: >4} > {channel.name}\n"
        return string+"```"
