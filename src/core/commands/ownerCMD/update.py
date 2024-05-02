import discord, sys, typing, asyncio, random
sys.dont_write_bytecode = True
from discord.ext import commands
from discord import app_commands
import src.connector as con


class Update(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.shared: con.Shared = con.shared
        self.bot: commands.Bot = bot

    @app_commands.command(name="fix_db", description="Owner command, no touchy!")
    async def owner(self, interaction: discord.Interaction) -> None:
        for guild in self.bot.guilds:
            self.shared.db.load_data(guild.id)
        await interaction.response.defer()

    @app_commands.command(name="update", description="Owner command, no touchy!")
    async def update(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        
        for guild in self.bot.guilds:
            if not (channel := guild.public_updates_channel) or not (channel := guild.system_channel):
                channel: discord.TextChannel = random.choice(guild.text_channels)
                
            embed: discord.Embed = discord.Embed(title="🔒 NoPing V3 Major Update", color=discord.Colour.dark_embed(),
                                                    description="Hey Owner, Admins and Mods,\n\nExciting news! NoPing V3 is here with major improvements in security, simplicity, and stability.")
            embed.add_field(name="`` What's New: ``", value="- **Revamped Architecture:** I've rebuilt the entire detection system from the ground up. Much better efficiency, stability & scalability.\
                                \n- **Simplified Configuration:** Almost everything is now under one command.  Featuring a user-friendly design & process.\
                                \n- **Fewer Commands:** Less is more! I've trimmed down the commands from a whopping 40+ to just 5 essentials.\
                                \n- **Futuristic look:** Clean & simple design, welcome to the future and goodbye to the past.", inline=False)
            embed.add_field(name="`` Important Stuff: ``", value="- **Database/Configuration Reset:** I've wiped the databases to ensure everything runs smoothly with the new setup. Sorry for any inconvenience and I hope this is the first and last wipe!\
                                \n- **Reporting Bugs:** Bugs happen, but with your help, we'll squash them! If you encounter any issues, please report them using the </noping:0> command.\
                                \n\nHave questions or need assistance? Don't hesitate to join my [support server](https://discord.gg/gzx3kxu68x).\
                                \n\n**PS:** *NoPing wanted to say something:*\nThanks a bunch for your ongoing support, and be sure to spread the word to your friends!\
                                \n\nStay secured.\n-Red", inline=False)
            await channel.send(content=f"{guild.owner.mention}", embed=embed)
            await asyncio.sleep(1.5)

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Update(bot), guild=discord.Object(id=1230040815116484678))
