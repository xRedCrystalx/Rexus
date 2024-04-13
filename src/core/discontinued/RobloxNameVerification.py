import discord, sys, aiohttp, asyncio
sys.dont_write_bytecode = True
import connector as syscon
from discord.ext import commands

class Buttons(discord.ui.View):
    def __init__(self) -> None:
        super().__init__(timeout=None)
        self.original_message: discord.InteractionMessage = None
        self.ReportedMessage: discord.Message = None
        
    @discord.ui.button(label="Delete message", style = discord.ButtonStyle.red)
    async def delete(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        try:
            await self.ReportedMessage.delete()
            await interaction.response.edit_message(view=None, embed=self.original_message.embeds[0].set_footer(text=f"Successfully deleted message. ({interaction.user.display_name})"))
        except Exception as error:
            await interaction.response.edit_message(view=None, embed=self.original_message.embeds[0].set_footer(text=f"Failed to delete message. ({interaction.user.display_name})"))

            
class RobloxNameVerification:
    def __init__(self) -> None:
        self.CONNECTOR: syscon.SysConnector = syscon.sys_connector
        self.bot: commands.Bot = self.CONNECTOR.bot
        self.filter: list[str] = ["username", "name", "love", "like", "best", "and", "ant", "creator", "user", "name", "thanks", "then", "try", "keep", "content", "good", "work", "man", "your"
                                  "best", "blade", "roblox", "bro", "real", "one", "sword", "big", "fan", "video", "can", "please", "cool", "videos", "vids", "new", "updates", "everyone", "from"
                                  "will", "upload", "always", "hard", "asking", "posting", "get", "subs", "you", "hope", "the", "this", "all", "our", "biggest", "youtuber", "subscribed", "thank",
                                  "message", "reading", "notifications", "anyway", "tbh", "recent", "funny", "ball", "updated", "have", "worst", "day", "making", "such", "since", "wait", "been"
                                  "favourite", "btw", "nice", "wassup", "post", "god", "life", "nick", "pls", "daily", "watch", "them", "its", "dream", "friend", "liked", "almost", "amazing", "that"
                                  "constantly", "youre", "discord", "every", "everyday", "fun", "shield", "years", "for", "more", "ive", "honestly", "doing", "brilliant", "let", "time", "out", "putting",
                                  "vibes", "such", "face", "blue", "red", "feel", "channel", "would", "was", "were", "bored", "covid", "win", "luck", "long", "think", "yours", "gonna", "main", "hello",
                                  "still", "matter", "supporting", "everyones", "account", "switch", "caps", "full", "halloween", "spin", "really", "said", "say", "mom", "vids", "viewers", "give", "used"
                                  "scanning", "fire", "makes", "smile", "speak", "acc", "bout", "ever", "back", "now", "recently", "noticed", "used", "anyways", "channels", "yall", "head", "watched", 
                                  "entertaining", "works", "keeps", "super", "display", "during", "stay", "joined", "instead", "mm2", "doesnt", "bad", "enjoy", "going", "whenever", "already", "any",
                                  "creators", "contents", "well", "not", "emojis", "plz", "supporter", "attachments", "alr", "bought", "much", "also", "sycthe", "nebula", "thats", "wishes", "having",
                                  "excellent", "trying", "reminder", "provided", "leveled", "watching", "because", "which", "want", "suggest", "pass", "item", "before", "need", "away", "purple", "given",
                                  "reward", "least", "raised", "anthappy", "found", "each", "they", "subscribing", "liking", "bladeball"]
        
        self.ratelimiter: list[discord.Message] = []
        self.bot.loop.create_task(self.verifier())

    async def respond(self, message: discord.Message) -> None:
        if message.channel.id == 1175142114376568882:
            self.ratelimiter.append(message)
        
        if message.content == "-rScan" and message.author.id == 333588605748510721:
            await message.channel.send("Scanning..")
            async for history_message in message.channel.history(limit=None, oldest_first=True):
                if not history_message.pinned:
                    self.ratelimiter.append(history_message)
    
    async def API_sender(self, word: str) -> dict:
        async with aiohttp.ClientSession() as session:
            response: aiohttp.ClientResponse = await session.get(f"https://users.roblox.com/v1/users/search?keyword={word}&limit=10")
            JSON: dict = await response.json()
            if JSON.get("errors"):
                #print("Waiting... ratelimits")
                await asyncio.sleep(10)
                return await self.API_sender(word=word)
            else:
                #print("Got content:", JSON)
                return JSON

    async def verifier(self) -> None:
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            while self.ratelimiter:
                message: discord.Message = self.ratelimiter[0]
                message_words: list[str] = message.content.replace(":", " ").split()
                ServerData: dict = self.CONNECTOR.database.load_data(server_id=message.guild.id, serverData=True)
                
                for word in message_words:
                    check = False
                    word: str = "".join([c for c in word if c.isalnum() or c == "_"])
                    #print("Sterlized word:", word)
                    if len(word) >= 3 and word.lower().strip() not in self.filter:
                        JSON: dict = await self.API_sender(word=word)
                        
                        if JSON.get("data"):
                            for user in JSON["data"]:
                                if user["name"].lower() == word.lower():
                                    roblox_id = user["id"]
                                    #print("Roblox ID found:", roblox_id)
                                    
                                    if ServerData["RobloxUsers"].get(str(roblox_id)):
                                        ServerData["RobloxUsers"][str(roblox_id)]["discord_id"].append(message.author.id) if message.author.id not in ServerData["RobloxUsers"][str(roblox_id)]["discord_id"] else None
                                        check = True
                                    else:
                                        ServerData["RobloxUsers"][str(roblox_id)] = {
                                            "roblox_name" : user["name"],
                                            "discord_id" : [message.author.id]
                                        }
                                    #print("Saved.")

                                    if check:
                                        channel: discord.TextChannel = message.guild.get_channel(711311257570902109)
                                        if channel:
                                            #print("Sending duplicate message")
                                            button = Buttons()
                                            embed = discord.Embed(title="Possible duplicate", color=discord.Colour.dark_theme())
                                            embed.add_field(name="`` INFO ``", value=f"**Roblox Username:** {ServerData['RobloxUsers'][str(roblox_id)]['roblox_name']}\n**Roblox ID:** {roblox_id}\n**Duplicated message:** [Message link]({message.jump_url})", inline=True)
                                            embed.add_field(name="`` Discord Accounts ``", value='\n- '.join([str(x) for x in ServerData['RobloxUsers'][str(roblox_id)]['discord_id']]), inline=True)
                                            embed.add_field(name="`` Message Content ``", value=f"{message.content if len(message.content) < 1000 else f'{message.content[:1000]}...'}", inline=False)
                                            embed.set_thumbnail(url=message.author.display_avatar)
                                            
                                            original_message: discord.Message = await channel.send(embed=embed, view=button)
                                            button.original_message = original_message
                                            button.ReportedMessage = message
                                            check = False

                self.CONNECTOR.database.save_data(server_id=message.guild.id, update_data=ServerData)
                self.ratelimiter.pop(0)

            await asyncio.sleep(1)