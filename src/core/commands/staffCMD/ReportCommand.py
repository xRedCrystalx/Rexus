import discord, sys, re, json
sys.dont_write_bytecode = True
from discord.ext import commands
from discord import app_commands
import src.connector as con


class buttonHandler(discord.ui.View):
    def __init__(self) -> None:
        super().__init__(timeout=60)
        self.shared: con.Shared = con.shared
        self.response: bool = False
        self.original_message: discord.InteractionMessage = None
        self.isClicked: bool = False
        self.ReportedMessage: discord.Message = None
        self.Reason: str = None
        self.Extra: str = None
        self.MessageLink = None

        
    @discord.ui.button(label = "Yes, send report to moderation team.", style = discord.ButtonStyle.green)
    async def buttonYes(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await interaction.response.edit_message(view=None, embed=self.original_message.embeds[0].set_footer(text="✅ Button YES was chosen. Sending report to discord's moderation team."))
        self.isClicked = True
        with open(f"{self.shared.path}/src/system/reports.json","r") as reportFile:
            data: list = json.load(reportFile)
            
        report: dict = {
                "ID" : self.shared._create_id(),
                "Report" : {
                    "Reason" : "Underage",
                    "User" : self.ReportedMessage.author.name,
                    "UserID" : self.ReportedMessage.author.id,
                    "MessageLink" : self.MessageLink,
                    "MessageContent" : self.ReportedMessage.content,
                    "Extra" : self.Extra  
                },
                "StaffMember" : {
                    "User" : interaction.user.name,
                    "UserID" : interaction.user.id,
                    "Guild" : interaction.guild.name,
                    "GuildID" : interaction.guild.id
                }
            }
            
        data.append(report)
        with open(f"{self.shared.path}/src/system/reports.json","w") as reportFile:
            json.dump(data, reportFile, indent=4)
        

    @discord.ui.button(label = "No, stop the report.", style = discord.ButtonStyle.red)
    async def buttonNo(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await interaction.response.edit_message(view=None, embed=self.original_message.embeds[0].set_footer(text="❌ Button NO was chosen. Stoping the request."))
        self.isClicked = True
        
    async def on_timeout(self) -> None:
        if self.original_message is not None and self.isClicked is False:
            await self.original_message.edit(view=None, embed=self.original_message.embeds[0].set_footer(text="⚠️ Timed out. Try again later."))
        

class ReportCommand(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.shared: con.Shared = con.shared
        self.bot: commands.Bot = bot
        self.c: con.Colors.C | con.Colors.CNone = self.shared.colors

    @app_commands.command(name="report", description="Report server member to discord.")
    async def report(self, interaction: discord.Interaction, message_link: str, age: int|None = None, extra: str | None = None) -> None:
        async def get_linked_message(link: str) -> discord.Message: 
            try:
                linkIDs: list[str] = link.replace("https://discord.com/channels/", "").split("/")
                get_guild: discord.Guild = self.bot.get_guild(int(linkIDs[0]))
                channel: discord.TextChannel = get_guild.get_channel(int(linkIDs[1]))
                message: discord.Message = await channel.fetch_message(int(linkIDs[2]))
                return message
            except Exception as error:
                return error
        
        def verify(targetMessageAge: int | None, targetAge: int | None, message: discord.Message) -> tuple:
            if targetAge is None and targetMessageAge is None:
                return (False, "❌ Could **not** find age in targeted message. Please input age in optional `age` field.")
    
            elif targetAge is not None and targetMessageAge is None:
                if targetAge > 0 or targetAge < 13:
                    if str(targetAge) in message.content:
                        return (True, targetAge)
                    else:
                        return (False, "❌ Could **not** find given age in targeted message. Please make sure that you provided right message link.")
                else:
                    return (False, "⚠️ Please input valid age between 1-13.")
                
            elif targetMessageAge is not None and targetAge is None:
                if targetMessageAge > 0 or targetMessageAge < 13:
                    return (True, targetMessageAge)
                else:
                    return (False, "⚠️ Please input valid age between 1-13.")
                
            else:
                if targetAge == targetMessageAge:
                    return (True, targetMessageAge)
                else:
                    return (False, "⚠️ Please make sure to input right age.")
        
        def get_age(text: str) -> int:
            verified_age: re.Match[bytes] | None = re.search(r"\b(1[0-2]|[1-9])\s*(?:y|years|yrs|old|yr?)\b", text, re.IGNORECASE)
            if verified_age is not None:
                age: re.Match[bytes] | None = re.search(r"\b(1[0-2]|[1-9])\b", verified_age.group(0))
                return int(age.group(0)) if age is not None else None
            else:
                return None
            
        BotData, ServerData = self.CONNECTOR.database.load_data(server_id=interaction.guild.id, serverData=True, botConfig=True)
        
        if (ServerData["ServerInfo"]["StaffRole"] in [x.id for x in interaction.user.roles]) or (interaction.user.id in [x for x in BotData["owners"]]):
            if not re.findall(r"https://discord.com/channels/[0-9]+/[0-9]+/[0-9]+", message_link):
                await interaction.response.send_message(content="Invalid message link.", ephemeral=True)
            else:
                message: discord.Message | Exception = await get_linked_message(link=message_link)
                if isinstance(message, discord.Message):
                    buttons = buttonHandler()
                    messageAge: int | None = get_age(text=message.content)
                    verification: tuple = verify(targetAge=age, targetMessageAge=messageAge, message=message)
                    if verification[0] is False:
                        await interaction.response.send_message(content=verification[1], ephemeral=True)
                    else:
                        real_age: int = verification[1]
                        embed=discord.Embed(title="Report Confirmation", description="Please carefully re-read created report. False reports will result to a command ban.", color=0xfff700)
                        embed.set_thumbnail(url=f"{message.author.avatar.url}")
                        embed.add_field(name="Reported User:", value=f"- **Name:** {message.author}\n- **ID:** {message.author.id}", inline=True)
                        embed.add_field(name="Extra:", value=f"{extra if extra else 'No extra information.'}", inline=True)
                        embed.add_field(name="Reason:", value=f"**ToS Violation:** Targeted user's age is under minimal required age.\n**Required:** 13y\n**User:** {real_age}y\n- **Targeted Message:** **[Jump to message]({message_link})**\n\n> **Message ID:** {message.id}\n> **Message Content:**\n> {message.content if len(message.content) < 700 else str(message.content[:(len(message.content)-((700-len(message.content))//-1))]) +'...'}", inline=False)
                        embed.set_footer(text="Waiting for button interaction...")
                        await interaction.response.send_message(embed=embed, view=buttons, ephemeral=True)
                        buttons.original_message = await interaction.original_response()
                        buttons.ReportedMessage = message
                        buttons.MessageLink = message_link
                        buttons.Extra = extra                        
                        await interaction.followup.send(content=f"?ban {message.author.id} Underage ({real_age}y old).", ephemeral=True) #
                else:
                    await interaction.response.send_message(content="An error has occured. Was message deleted?", ephemeral=True)   
        else:
            await interaction.response.send_message(content="You do not have permissions to execute this command.", ephemeral=True)

        self.shared.logger.log(f"{self.c.Magenta}{interaction.user.name} ({interaction.user.id}){self.c.R} used {self.c.Yellow}/report{self.c.R} slash command. {self.c.DBlue}Guild{self.c.R}: {interaction.guild.name}")

async def setup(bot: commands.Bot) -> None:
    #await bot.add_cog(ReportCommand(bot))
    pass

#CHECK: if it even fucking works
