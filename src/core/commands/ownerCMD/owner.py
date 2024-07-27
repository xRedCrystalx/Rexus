import discord, sys, typing
sys.dont_write_bytecode = True
from discord.ext import commands
from src.connector import shared

class OwnerCMD(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot) -> None:
        self.bot: commands.AutoShardedBot = bot

    @discord.app_commands.choices(cmd=[
        discord.app_commands.Choice(name="sync", value="sync"),
        discord.app_commands.Choice(name="shutdown", value="shutdown"),
        discord.app_commands.Choice(name="logging_level", value="logging_level")
        ]
    )
    @discord.app_commands.command(name="owner", description="Owner commands, no touchy!")
    async def owner(self, interaction: discord.Interaction, cmd: discord.app_commands.Choice[str], args: str = None) -> None:
        await interaction.response.defer(thinking=True, ephemeral=True)

        if True:#check_bot_owner(interaction.user.id):
            func: typing.Callable = getattr(self, cmd.value)
            await func(interaction=interaction, args=args)
        else:
            await interaction.followup.send("You do not have permissions to execute this command.", ephemeral=True)

    async def sync(self, interaction: discord.Interaction, args: str | None) -> None:
        try:
            if args:
                await shared.bot.tree.sync(guild=discord.Object(id=int(args)))
                await interaction.followup.send(f"Successfully synced commands to guild: {args}", ephemeral=True)
            else:
                if await shared.bot.tree.sync():
                    await interaction.followup.send("Sucessfully synced globally.", ephemeral=True)
                else:
                    raise Exception("Not synced/0 commands?")

        except Exception as error:
            await interaction.followup.send(f"Syncing failed > {type(error).__name__}: {error}", ephemeral=True)
            shared.logger.log(f"@NoPing.sync > Failed to sync.\n```{type(error).__name__}: {error}```", "ERROR")

    async def shutdown(self, interaction: discord.Interaction, args: str | None) -> None:
        await interaction.followup.send("Restarting..", ephemeral=True)
        await shared.bot.close()

    async def logging_level(self, interaction: discord.Interaction, args: str | None) -> None:
        try:
            if not args:
                raise ValueError("No args specified")
            
            if len(arguments := args.split("=")) != 2:
                raise ValueError("Not enough arguments")
    
            if arguments[0].lower() == "console":
                var: str = "CONSOLE_LEVEL"
            else:
                var: str = "FILE_LEVEL"

            setattr(shared.logger, var, int(arguments[1]))
            shared.reloader.reload_module("Logger")

            await interaction.followup.send(f"Successfully applied new logging level `{args}`", ephemeral=True)
        
        except Exception as error:
            await interaction.followup.send(f"Failed to update logging level: `{args}`.\n```{type(error).__name__}: {error}```", ephemeral=True)
            shared.logger.log(f"@NoPing.logging_level > {type(error).__name__}: {error}", "ERROR")

async def setup(bot: commands.AutoShardedBot) -> None:
    await bot.add_cog(OwnerCMD(bot), guild=discord.Object(id=1230040815116484678))
