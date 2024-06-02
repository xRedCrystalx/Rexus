import discord, urllib.parse, sys, typing, random, aiohttp
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
            "What do you get from a pampered cow? Spoiled milk!",
            "What do you call a bee that comes from America? A USB!",
            "I went to the aquarium this weekend, but I didn't stay long. There's something fishy about that place.",
            "What's a cat's favorite instrument? Purr-cussion.",
            "What subject do cats like the most in school? Hiss-tory.",
            "My boss said \"dress for the job you want, not for the job you have.\" So I went in as Batman.",
            "How do you make holy water? You boil the hell out of it.",
            "I can always tell when someone is lying. I can tell when they're standing too.",
            "Some people pick their nose, but I was born with mine.",
            "I used to be afraid of speed bumps. I'm trying to get over it.",
            "If your house is cold, just stand in the corner. It's always 90 degrees there.",
            "I found a book called *How to Solve 50% of Your Problems*. So I bought 2.",
            "Did you hear about the new squirrel diet? It's just nuts.",
            "I made song about tortilla once, now it's more like a wrap.",
            "I was going to tell you a joke about boxing but I forgot the punch line.",
            "Why did the egg hide? It was a little chicken.",
            "What kind of candy do astronauts like? Mars bars.",
            "I ordered a chicken and an egg from Amazon. I'll let you know. (Context: What came first? The globally known question.)",
            "What do you call it when a snowman throws a tantrum? A meltdown.",
            "My uncle named his dogs Timex and Rolex. They're his watch dogs.",
            "Which is faster, hot or cold? Hot, because you can catch cold.",
            "What do you call a pig that does karate? A pork chop.",
            "I'm so good at sleeping I can do it with my eyes closed!",
            "What happens when a strawberry gets run over crossing the street? Traffic jam.",
            "How do celebrities stay cool? They have many fans.",
            "How did the student feel when he learned about electricity? Totally shocked.",
            "What do you call a bee that can't make up its mind? A Maybe.",
            "What do you call a hippie's wife? Mississippi.",
            "What did one wall say to the other? I'll meet you at the corner.",
            "Did you hear the rumor about butter? Well, I'm not going to spread it.",
            "Why did the student eat his homework? Because his teacher told him it was a piece of cake.",
            "I couldn't figure out why the baseball kept getting larger. Then it hit me.",
            "Did you hear the one about the roof? Never mind, it's over your head.",
            "What's a ninja's favorite type of shoes? Sneakers."
        ]

    async def ask_ai(self, guild_db: dict[str, typing.Any], bot_db: dict[str, typing.Any], message: discord.Message, **OVERFLOW) -> None: 
        if guild_db["ai"]["status"] and message.channel.id in guild_db["ai"]["talkChannels"]:
            if message.content.startswith("> "):
                async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(5000)) as session:
                    response: aiohttp.ClientResponse = await session.get(f"http://api.brainshop.ai/get?bid=168684&key=lkrMGm9sSb22jqSG&uid={message.author.id}&msg={urllib.parse.quote(message.clean_content[2:])}", headers=self.header)
                
                if response.status != 200:
                    self.shared.logger.log(f"AI: API call failed. {response.reason} {response.status}", "WARNING")

                try:
                    JSONreply: dict[str, str] = await response.json()
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

                    self.shared.sender.resolver(con.Event(message.channel, "send", event_data={"kwargs": {"content": filtered}}))

            elif "<@980031906836009000>" in message.content or "noping" in message.content.lower() or "no ping" in message.content.lower():
                embed: discord.Embed = discord.Embed(title="Hey there!", color=discord.Colour.dark_embed(), description="To talk to me, use `> ` infront of message!\nHere is an example: `> Hey, how are you!`")
                self.shared.sender.resolver(con.Event(message.channel, "send", event_data={"kwargs": {"embed": embed}}))
        return None
