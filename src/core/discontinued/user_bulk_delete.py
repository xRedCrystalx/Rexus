import discord, sys, typing
sys.dont_write_bytecode = True
from discord.ext import commands
from discord import app_commands
import src.connector as con


class BulkDelete(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.shared: con.Shared = con.shared
        self.bot: commands.Bot = bot
        self.c: con.Colors.C | con.Colors.CNone = self.shared.colors

    @app_commands.command(name="purge", description="Purges user's messages.")
    async def purge(self, interaction: discord.Interaction, member: discord.Member, number: int | None = None) -> None:
        guild_db: dict[str, typing.Any] = self.shared.db.load_data(interaction.guild.id)
        bot_config: dict[str, typing.Any] = self.shared.db.load_data()

        def target(m: discord.Message) -> bool:
            return m.author.id == member.id

        if guild_db["general"]["staffRole"] in [x.id for x in interaction.user.roles] or interaction.user.id in bot_config["owners"]:
            try:
                await interaction.response.send_message(f"Purging {member.display_name}'s messages of last {number if number else '100'} messages per channel.")
                
                for channel in interaction.guild.text_channels:
                    await channel.purge(limit=number, check=target)
             
                await interaction.followup.send(f"Successfully purged {member.display_name}'s messages from all channels.")
                self.shared.logger.log(f"{self.c.Magenta}{interaction.user.name} ({interaction.user.id}){self.c.R} used {self.c.Yellow}/purge{self.c.R} slash command. {self.c.DBlue}Input{self.c.R}: member: {member.display_name} ({member.id}) number: {number} {self.c.DBlue}Guild{self.c.R}: {interaction.guild.name}")                
                    
            except Exception as error:
                id: str = self.shared._create_id()
                await interaction.response.send_message(f"Failed to purge {member.display_name}'s messages. Error ID: `{id}`", ephemeral=True)
                self.shared.logger.log(f"{self.c.Magenta}{interaction.user.name} ({interaction.user.id}){self.c.R} failed to use {self.c.Yellow}/purge{self.c.R} slash command. {self.c.DBlue}Input{self.c.R}: member: {member.display_name} ({member.id}) number: {number} {self.c.DBlue}Guild{self.c.R}: {interaction.guild.name} {self.c.DBlue}ID{self.c.R}: {self.c.Red}{id} \nError: {type(error).__name__}: {error}", "ERROR")
        else:
            await interaction.response.send_message("You do not have permissions to execute this command.", ephemeral=True)
            self.shared.logger.log(f"{self.c.Magenta}{interaction.user.name} ({interaction.user.id}){self.c.R} tried to use {self.c.Yellow}/purge{self.c.R} slash command. {self.c.DBlue}Input{self.c.R}: member: {member.display_name} ({member.id}) number: {number} {self.c.DBlue}Guild{self.c.R}: {interaction.guild.name}")

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(BulkDelete(bot))