import discord, requests, urllib.parse, sys, typing, random
sys.dont_write_bytecode = True
import src.connector as con

class AI:
    def __init__(self) -> None:
        self.shared: con.Shared = con.shared
        self.header: dict[str, str] = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36"}
        self.jokes: list[str] = [
            "Hear about the new restaurant called Karma? There's no menu: You get what you deserve.",
            "How do you organize a space party? You planet.",
            "When does a joke become a 'dad' joke? When it becomes apparent.",
            "What did 1 tomato say to the other tomato while running? You better ketchup!",
            "What did the janitor say when he jumped out of the closet? Supplies!",
            "Wanna know why I'm standing on this clock? It's because I want to be on time!",
            "What kind of dog does the timekeeper has? A watchdog!",
            "I used to play piano by ear. Now I use my hands.",
            "What did the vet say to the cat? How are you feline?",
            "What do you call a 100 year old ant? An antique!",
            "What's brown and sticky? A stick!",
            "What does James Bond do before bedtime? He goes undercover!",
            "What do you get from a pampered cow? Spoiled milk!"
        ]

    async def ask_ai(self, guild_db: dict[str, typing.Any], bot_db: dict[str, typing.Any], message: discord.Message, **OVERFLOW) -> None: 
        if guild_db["ai"]["status"] and message.channel.id in guild_db["ai"]["talkChannels"]:
            if message.content.startswith("> "):
                response: requests.Response = requests.get(f"http://api.brainshop.ai/get?bid=168684&key=lkrMGm9sSb22jqSG&uid={message.author.id}&msg={urllib.parse.quote(message.content[2:])}", headers=self.header)
                try:
                    JSONreply: dict[str, str] = response.json()
                except:
                    JSONreply: dict[str, str] = {"cnt" : "[INFO] Oh no, something went wrong! Corrupted response."}

                if text := JSONreply.get("cnt"):
                    if [word for word in ["http://", "https://"] if word in text]:
                        filtered: str = "[Filter] Sorry, but AI is not allowed to send links."
                    elif [word for word in bot_db["filters"]["message"]["bad_words"] if str(word).lower() in text.lower()]:
                        filtered: str = "[Filter] Sorry, but AI is not allowed to say bad words."
                    elif text == "[JOKE]":
                        filtered: str = self.jokes[random.randint(0, len(self.jokes)-1)]
                    else:
                        filtered: str = text

                    self.shared.sender.resolver(con.Event(message.channel, "send", event_data={"content": filtered}))

            elif "<@980031906836009000>" in message.content or "noping" in message.content.lower() or "no ping" in message.content.lower():
                embed: discord.Embed = discord.Embed(title="Hey there!", color=discord.Colour.dark_embed(), description="To talk to me, use `> ` infront of message!\nHere is an example: `> Hey, how are you!`")
                self.shared.sender.resolver(con.Event(message.channel, "send", event_data={"embed": embed}))
        return None
