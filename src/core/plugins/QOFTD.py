import schedule, sys, discord, random, asyncio, typing
sys.dont_write_bytecode = True
import src.connector as con

if typing.TYPE_CHECKING:
    from discord.ext import commands

class QOFTD:
    def __init__(self) -> None:
        self.shared: con.Shared = con.shared
        self.bot: commands.Bot = self.shared.bot
        self.current_msgs: dict[int, discord.Message] = {}
        self.loop: asyncio.AbstractEventLoop = asyncio.get_running_loop()

        self.quotes: list[str] = ["Would you allow someone to throw garbage over your head in return for a $100 reward?",
                              "What would you do when you reach your school or workplace and realize that you forgot to have a bath before coming?",
                              "Would you ever think of pranking your teacher/boss?",
                              "Suppose you go to a restaurant all alone and eat a lot only to realize that you have forgotten your wallet back at home, what would you do?",
                              "Do you have a habit of sleeping with a plush toy or hugging a pillow while asleep?", "Tell us the most hilarious thing ever that you have witnessed or experienced.",
                              "Do you enjoy bursting bubbles on bubble wrap paper? If yes, how many bubbles have you burst in one go?",
                              "If you were a worm, how long would you be?",
                              "Would you jump 15 feet high up in the air of 15 feet far?",
                              "If someone asks you to count backward from 10,000 to 0 in return for a special reward, will you do it?",
                              "Which tongue twister is your favorite?",
                              "What is the funniest thing that you have ever done?",
                              "If you could have any fictional character as your personal assistant for a day, who would it be and what tasks would you assign them?",
                              "If you were to open a restaurant with a ridiculous theme, what would the theme be and what type of food would you serve?",
                              "If you could replace handshakes with a new, funny greeting, what would it be and how would you demonstrate it?",
                              "If you were given the ability to rename any city in the world, which city would you choose and what would you rename it to?",
                              "If you were to compete in the Olympics but could only participate in a made-up event, what would your event be called and how would it work?",
                              "If you could only wear one type of hat for the rest of your life, what would it be and why?",
                              "If you had the chance to star in a movie, but it had to be a parody of a famous film, which movie would you choose and what would the parody be called?",
                              "If you were to write a book about your life but had to give it a funny title, what would the title be?",
                              "If you had to give a TED Talk on a completely nonsensical topic, what would the topic be and what would your main points be?",
                              "If you could turn any chore into a fun game, which chore would it be and how would you make it entertaining?",
                              "If you could create a new word that would be added to the dictionary, what would it be and what would it mean?",
                              "If you could only eat one type of food for the rest of your life, but it had to be something silly, what would you choose?",
                              "If you could invent a new holiday that celebrates something completely ridiculous, what would the holiday be called and how would people celebrate it?",
                              "If you could transform into any inanimate object for a day, what would you choose to be and why?",
                              "If you could be the world's best at any unusual skill or talent, what would it be and how would you use it to your advantage?",
                              "What is your favorite subject and least favorite subject to study?",
                              "What kind of community service would you like to be a part of?",
                              "Just an hour before your exam, you discover that you have prepared for the wrong subject. What would you do?",
                              "Have you ever gone off to sleep in class during a lecture?",
                              "Which games have you played with your friends during an ongoing class?",
                              "If you were to write a book, what would be your main subject?",
                              "One fine morning, if you happen to discover an alien spaceship in your backyard, what would you do?",
                              "If you chance upon a magical tree that could grow any food, what would you want to grow?",
                              "If you had a choice of eating an entire raw onion or a complete raw radish, which one would you eat?",
                              "If you had the opportunity to travel backward in time and meet someone, whom would you like to meet?",
                              "If at all you happen to forget your lines in a stage performance, what would you do?",
                              "If you were part of a circus troupe, what would you like to do?",
                              "If two of your best friends fight, how would you resolve the conflict?",
                              "Would you like to have a swimming race with a dolphin or a shark?",
                              "Would you like to become invisible or super strong?",
                              "If you could fly, how would you make good use of it?",
                              "If you could spend a whole day with someone, who would that person be?",
                              "Would you rather win $500 or allow your best friend to win $1000?",
                              "Would you rather walk amongst zombies or mummies? Why?",
                              "Which meal would you like to stop eating forever: breakfast, lunch, or dinner?",
                              "What do you like to do in your free time?",
                              "Do you like reading books or watching cartoons?",
                              "Did you learn anything new today?",
                              "When given a choice between candy and pizza, which one would you pick?",
                              "Did you help anyone in need today?",
                              "What good deed have you done today?",
                              "What is your favorite time of the day? Morning, afternoon, evening, or night?",
                              "Which is your favorite board game?",
                              "What is your favorite sports activity?",
                              "What is your favorite video game?",
                              "Who is your favorite superhero?",
                              "Do you like the summers, winters, autumn, or spring?",
                              "Which animal would you prefer to keep as a pet?",
                              "Who is your favorite Disney character?",
                              "What is your favorite book?",
                              "What makes you angry?",
                              "What activities do you do together with your family?",
                              "Where do you like to go during your vacations?",
                              "If animals could talk, which one do you think would have the best jokes and why?",
                              "If you could invent a new ice cream flavor, what would it be called and what ingredients would you use?",
                              "If you could create a new holiday, what would it be called and how would people celebrate it?",
                              "If you could have a superpower for a day, but it could only be something silly, what would you choose and why?",
                              "If you could switch places with any cartoon character for a day, who would it be and what would you do?",
                              "If you had to live in a house made of food, what type of food would you choose and why?",
                              "If you were a secret agent with a silly code name, what would your code name be and what would your secret mission be?",
                              "If you could make a new rule for your school, but it had to be something funny, what would it be?",
                              "If you were the ruler of a new planet, what funny laws would you create for your alien subjects to follow?",
                              "If you had a pet dinosaur, what would you name it and how would you take care of it?",
                              "If you could only wear one color of clothing for the rest of your life, which color would you choose?",
                              "Which place on Earth would you like to visit at least once in your lifetime?",
                              "Who has been your biggest motivation?",
                              "Which movie has inspired you the most?",
                              "Are you a sports lover or a movie buff?",
                              "What would you do if you had 24 hours all to yourself without anything important to do?",
                              "Do you love riding bikes or prefer to ride a horse?",
                              "What is that moment when you felt you had accomplished something great in life?",
                              "Would you love to party on a Friday night or prefer staying indoors and watch your favorite movie?",
                              "Which author's books fascinate you the most?",
                              "Do you like rock music or soft music?",
                              "According to you, what is more important, intelligence or beauty?",
                              "If you had the option to eat only one meal for an entire day, what would you choose to eat?",
                              "What would you do if you were the only human left on this planet?",
                              "Would you prefer having only one loyal friend or five casual friends?",
                              "Do you have any wish within you that you have been wanting to do for a long time but haven't been able to do so?",
                              "What would you do to make this world a better place to live?",
                              "Which food did you hate as a little kid but love eating now?",
                              "What is the dumbest thing that you have done?",
                              "Given a choice, what kind of gadget would you like to invent?",
                              "What is the topmost item on your bucket list?",
                              "If animals could talk, which would be the most boring one?",
                              "Which is the worst song you have ever heard?",
                              "Would you prefer being just 1 foot tall or 100 feet tall?",
                              "If you were stuck on a deserted island and could only bring three things with you, what would they be?",
                              "Have any of your dreams turned into reality?",
                              "Have you ever seen a ghost?",
                              "What is it that even your parents don't know about you?",
                              "If you had to describe yourself in just three words, what would those words be?",
                              "What do you think would happen on Earth if human beings could become immortal?",
                              "Where do you think dictionary writers got their word list from?",
                              "What do you think would have happened if humans existed on Mars instead of Earth?",
                              "Are you a leader or a follower?",
                              "What has been your favorite Wikipedia page so far?",
                              "Which habit of yours has gotten you into big trouble?",
                              "Why do you think you cry during uncontrollable laughter?",
                              "What do you think is the meaning of life?",
                              "What do you think the world will look like in the next 500 years?"]

    async def handle_quote(self, channel_id: int) -> None:
        try:
            channel: discord.TextChannel = self.bot.get_channel(channel_id)
            if channel_id:
                if self.current_msgs.get(channel_id):
                    await self.shared.sender.resolver([{self.current_msgs[channel_id] : {"action" : "unpin"}}])

                self.current_msgs[channel_id] = await channel.send(self.quotes[random.randint(0, len(self.quotes)-1)])
                await self.shared.sender.resolver([{self.current_msgs[channel_id] : {"action" : "pin"}}])
        
        except Exception as error:
            self.shared.logger.log(f"@QOFTD.handle_quote: {type(error).__name__}: {error}", "ERROR")

    def loader(self) -> None:
        try:
            for guild in self.bot.guilds:
                db: dict[str, typing.Any] = self.shared.db.load_data(guild.id)
                
                if db["QOFTD"]["status"] and (channel_id := db["QOFTD"]["log_channel"]):
                    self.loop.create_task(self.handle_quote(channel_id=channel_id))

        except Exception as error:
            self.shared.logger.log(f"@QOFTD.loader: {type(error).__name__}: {error}", "ERROR")
    
    async def start(self) -> None:
        await self.bot.wait_until_ready()
        schedule.clear()
        schedule.every().day.at("00:00").do(self.loader)
        while True:
            schedule.run_pending()
            await asyncio.sleep(1)
