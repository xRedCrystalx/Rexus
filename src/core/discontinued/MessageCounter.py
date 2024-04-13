import discord, sys, typing
sys.dont_write_bytecode = True
from discord.ext import commands
from discord import app_commands
import src.connector as con


class CountMessagesCommand(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.shared: con.Shared = con.shared
        self.bot: commands.Bot = bot
        self.c: con.Colors.C | con.Colors.CNone = self.shared.colors

        self.database: dict[int, dict[str, discord.Member | int]] = {}
        self.embeds: list[discord.Embed] = []

    @app_commands.command(name = "msg_count", description = "Counts how many messages were sent by a member in the channel.")
    async def ping(self, interaction: discord.Interaction) -> None:
        guild_db: dict[str, typing.Any] = self.shared.db.load_data(interaction.guild.id)
        bot_config: dict[str, typing.Any] = self.shared.db.load_data()

        if (guild_db["ServerInfo"]["StaffRole"] in [x.id for x in interaction.user.roles]) or (interaction.user.id in [x for x in bot_config["owners"]]):
            
            await interaction.response.send_message("Loading.. Please wait.")
            original_message: discord.InteractionMessage = await interaction.original_response()
            
            async for msg in interaction.channel.history(limit=None, oldest_first=True):
                if self.database.get(msg.author.id):
                    self.database[msg.author.id]["counter"] += 1
                else:
                    self.database[msg.author.id] = {
                        "member" : msg.author,
                        "counter" : 1
                    }
                
            if self.database != {}:
                MEMBERs: list[discord.Member] = []
                IDs: list[int] = []
                COUNTERs: list[int] = []
                
                for i, (ID, data) in enumerate(self.database.items()):
                    MEMBERs.append(data["member"])
                    IDs.append(ID)
                    COUNTERs.append(data["counter"])
                    
                    if i+1 % 25 == 0:
                        embed = discord.Embed(title="User List", color=discord.Colour.dark_embed(), timestamp=await self.CONNECTOR.callable(fun="datetime"))
                        embed.add_field(name="`` Member Name ``", value="\n".join([member.display_name for member in MEMBERs]))
                        embed.add_field(name="`` Member ID ``", value="\n".join(str(id) for id in IDs))
                        embed.add_field(name="`` Message Count ``", value="\n".join(str(counter) for counter in COUNTERs))
                        self.embeds.append(embed)
                        
                        MEMBERs, IDs, COUNTERs = ([], [], [])
                else:
                    embed = discord.Embed(title="User List", color=discord.Colour.dark_embed(), timestamp=await self.CONNECTOR.callable(fun="datetime"))
                    embed.add_field(name="`` Member Name ``", value="\n".join([member.display_name for member in MEMBERs]))
                    embed.add_field(name="`` Member ID ``", value="\n".join(str(id) for id in IDs))
                    embed.add_field(name="`` Message Count ``", value="\n".join(str(counter) for counter in COUNTERs))
                    self.embeds.append(embed)

                try:
                    buttonHandler = await self.CONNECTOR.callable(fun="buttonHandler", timeout=60 * 10)
                    
                    print(self.embeds)
                    await original_message.edit(content=None, embed=discord.Embed(title="User List", description="Use arrows to navigate"), view=buttonHandler.create_paginator(messages=self.embeds))
                    buttonHandler.original_message = original_message
                    await self.CONNECTOR.logging(logType="INFO", data=f"{self.c.Magenta}{interaction.user.name} ({interaction.user.id}){self.c.R} used {self.c.Yellow}/msg_count{self.c.R} slash command. Guild{self.c.R}: {interaction.guild.name}")
                    
                except Exception as error:
                    id: str = await self.CONNECTOR.callable(fun="error_id")
                    await original_message.edit(f"Failed to count messages. Error ID: {id}", ephemeral=True)
                    await self.CONNECTOR.logging(logType="ERROR", data=f"{self.c.Magenta}{interaction.user.name} ({interaction.user.id}){self.c.R} failed to use {self.c.Yellow}/msg_count{self.c.R} slash command. {self.c.DBlue}Guild{self.c.R}: {interaction.guild.name} {self.c.DBlue}ID{self.c.R}: {self.c.Red}{id} \nError: {type(error).__name__}: {error}")
            else:
                await original_message.edit("Counting failed. Please notify xRedCrystalx. Thanks!", ephemeral=True)
        else:
            await interaction.response.send_message("You do not have permissions to execute this command.", ephemeral=True)
            await self.CONNECTOR.logging(logType="WARNING", data=f"{self.c.Magenta}{interaction.user.name} ({interaction.user.id}){self.c.R} tried to use {self.c.Yellow}/msg_count{self.c.R} slash command. {self.c.DBlue}Guild{self.c.R}: {interaction.guild.name}")
    
            
async def setup(bot: commands.Bot) -> None:
    pass
    #await bot.add_cog(CountMessagesCommand(bot))