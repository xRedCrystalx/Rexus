import discord, sys, re
sys.dont_write_bytecode = True
from discord.ext import commands
from discord import app_commands
import src.connector as con


class Input(discord.ui.Modal, title="Link Legitimacy Checker"):
    def __init__(self) -> None:
        self.shared: con.Shared = con.shared
        super().__init__(timeout=None) 

    #ser_id = discord.ui.TextInput(label="ID of suspected user:", placeholder="Input user ID here.", style=discord.TextStyle.short, required=False)
    sus_message = discord.ui.TextInput(label="Suspected message content/link:", placeholder="Input message content with suspected link or link alone.", style=discord.TextStyle.long, min_length=1, max_length=4000, required=True)

    async def on_submit(self, interaction: discord.Interaction) -> None:
        ServerData: dict =  self.shared.db.load_data(interaction.guild.id)
        db: dict[str, dict[str | None, bool]] = {}
        
        masked_links: list[str] = re.findall(pattern=r'\[(.*?)\]\((https?://\S+?)\)', string=self.sus_message.value)
        masked_removed: str = re.sub(pattern=r'\[(.*?)\]\((https?://\S+?)\)', repl="", string=self.sus_message.value)
            
        normal_links: list[str] = re.findall(pattern=r"https?\:\/\/[^\n\r\s\t]*", string=masked_removed)
        
        for mask, real in masked_links:
            if real not in db.keys():
                if real.startswith("https://www.roblox.com") or real.startswith("https://roblox.com"):
                    db.update({real : {"mask" : mask, "safe" : True}})
                else:
                    db.update({real : {"mask" : mask, "safe" : False}})
                
        for link in normal_links:
            if link not in db.keys():
                if link.startswith("https://www.roblox.com") or link.startswith("https://roblox.com"):
                    db.update({link : {"mask" : None, "safe" : True}})
                else:
                    db.update({link : {"mask" : None, "safe" : False}})
        
        if db:
            embed: discord.Embed = discord.Embed(title="Found links", description="Checking links for roblox.com", color=discord.Colour.dark_embed(), timestamp=self.shared._datetime())
            embed.add_field(name="`` Original Links: ``", value="- "+"\n- ".join([f"{x} > {'`ROBLOX`' if db[x]['safe'] else '`NOT ROBLOX`'}" for x in db.keys()]), inline=True)
            embed.add_field(name="`` Masked As: ``", value="- "+"\n- ".join([str(db[x]["mask"]) for x in db.keys()]), inline=True)
            embed.set_footer(text="Make sure to report the user to staff team!")
        else:
            embed: discord.Embed = discord.Embed(title="No links found..", description="Could not find any links in the provided message.", color=discord.Colour.dark_embed(), timestamp=self.shared._datetime())
            embed.set_footer(text="Possibly a bug? Report it to xRedCrystalx!")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        await interaction.response.send_message('Oops! Something went wrong. Ping xRedCrystalx!', ephemeral=True)

class LinkLegitimacyCommand(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.shared: con.Shared = con.shared
        self.bot: commands.Bot = bot

    @app_commands.command(name = "link_legitimacy", description = "Scans whole message content for links and determinates legitimacy.")
    async def legit(self, interaction: discord.Interaction) -> None:
        await interaction.response.send_modal(Input())
            
async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(LinkLegitimacyCommand(bot))