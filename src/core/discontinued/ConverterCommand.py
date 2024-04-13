import discord, sys
sys.dont_write_bytecode = True
from discord.ext import commands
from discord import app_commands


class ConverterCommand(commands.Cog):
    @app_commands.choices(option=[
        app_commands.Choice(name="°C to °F", value="ctof"),
        app_commands.Choice(name="°F to °C", value="ftoc"),
        ])
    @app_commands.command(name="converter", description="Converts values from one measurement to other (Supports only °F to °C and reverse).")
    async def conventer(self, interaction: discord.Interaction, option: app_commands.Choice[str], value:int) -> None:
        match option.value:
            case "ctof":
                await interaction.response.send_message(f"**[Converter]** `{value}°C`  **->**  `{round((value*9/5)+32, 2)}°F`")
            case "ftoc":
                await interaction.response.send_message(f"**[Converter]** `{value}°F`  **->**  `{round((value-32)*5/9, 2)}°C`")

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(ConverterCommand())