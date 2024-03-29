import discord, sys, typing
sys.dont_write_bytecode = True
from discord.ext import commands
from discord import app_commands
import src.connector as con

db: dict[str, int | discord.Embed, list] = {
    "embed" : None,
    "options" : 0,
    "emoji" : [r"1️⃣", r"2️⃣", r"3️⃣", r"4️⃣", r"5️⃣", r"6️⃣", r"7️⃣", r"8️⃣", r"9️⃣", r"🔟"],
    "question" : None
}

class Button(discord.ui.View):
    def __init__(self, *, timeout: float | None = None, current: int) -> None:
        self.current: int = current
        super().__init__(timeout=timeout)

    @discord.ui.button(label = "Continue!", style = discord.ButtonStyle.green)
    async def buttonNo(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        inp = Input(current=self.current+5)
        [inp.add_item(discord.ui.TextInput(label=f"Option {x+1}", placeholder="Write poll option here!", style=discord.TextStyle.short, required=True, max_length=256)) for x in range(self.current+5, db["options"] if db["options"]-self.current+5 <= 5 else self.current+10)]
            
        await interaction.response.send_modal(inp)

class Input(discord.ui.Modal, title="Poll configuration"):
    def __init__(self, current: int) -> None:
        self.shared: con.Shared = con.shared
        self.current: int = current
        super().__init__(timeout=None)
        
    async def _send(self, interaction: discord.Interaction, embed: discord.Embed) -> None:
        db["embed"].set_footer(text=f"Hosted by {interaction.user.display_name}")
        await interaction.response.send_message(embed=db["embed"])
        
        msg: discord.InteractionMessage = await interaction.original_response()
        for num in range(db["options"]):
            await msg.add_reaction(db["emoji"][num])
    
    async def on_submit(self, interaction: discord.Interaction) -> None:
        if self.current == 0:
            db["embed"] = discord.Embed(title=db["question"], color=discord.Colour.dark_embed(), timestamp=self.shared._datetime())
        
        if data := interaction.data.get("components"):
            for i, component in enumerate(data[self.current:], self.current):
                db["embed"].add_field(name=component["components"][0]["value"], value=f"React with {db['emoji'][i]}", inline=False)
                
        if self.current+5 >= db["options"]:
            await self._send(interaction=interaction, embed=db["embed"])
        else:
            btn = Button(current=self.current)
            await interaction.response.send_message("Click on the button to continue with configuration. Only way to bypass discord's limitations.", view=btn, ephemeral=True)

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        await interaction.response.send_message(f'Oops! Something went wrong. {error}', ephemeral=True)

class TestPollCommand(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.shared: con.Shared = con.shared
        self.bot: commands.Bot = bot
        self.c: con.Colors.C | con.Colors.CNone = self.shared.colors

    @app_commands.command(name = "poll_test", description = "for RED only. DO NOT USE")
    async def responder(self, interaction: discord.Interaction, question: str, option_num: int) -> None:
        guild_db: dict[str, typing.Any] = self.shared.db.load_data(interaction.guild.id)
        bot_config: dict[str, typing.Any] = self.shared.db.load_data()
        
        if interaction.user.id in bot_config["owners"]:
            if option_num < 1 and option_num > 10:
                await interaction.response.send_message("Input number between 1 and 10")
                
            if len(question) > 256:
                await interaction.response.send_message("Question can be maximum of 256 letters long. (discord limitation)")

            inp = Input(current=0)
            [inp.add_item(discord.ui.TextInput(label=f"Option {x+1}", placeholder="Write poll option here!", style=discord.TextStyle.short, required=True, max_length=256)) for x in range(option_num if option_num <= 5 else 5)]
            db["question"] = question
            db["options"] = option_num
            
            await interaction.response.send_modal(inp)
        else:
            await interaction.response.send_message("You do not have permissions to execute this command.", ephemeral=True)
            
async def setup(bot: commands.Bot) -> None:
    pass
    #await bot.add_cog(TestPollCommand())
