import discord, sys, ast, asyncio
sys.dont_write_bytecode = True
from discord.ext import commands
import src.connector as con


class ExecuteCommandOwner(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.shared: con.Shared = con.shared
        self.bot: commands.Bot = bot
        self.c: con.Colors.C | con.Colors.CNone = self.shared.colors
        self.original_stdout = sys.stdout

    @commands.command(name="execute")
    async def execute(self, ctx: commands.Context) -> list:
        def execute_python_code(code: str) -> list:
            class CustomStdout:
                def __init__(self) -> None:
                    self.output: list = []

                def write(self, text) -> None:
                    self.output.append(text)

            custom_stdout = CustomStdout()
            sys.stdout = custom_stdout

            try:
                exec(compile(ast.parse(code), filename='<ast>', mode='exec'), global_vars, {'print': print})
            except Exception as error:
                print(error)

            sys.stdout = self.original_stdout
            return custom_stdout.output

        BotData: dict = self.shared.db.load_data()
        if ctx.author.id in [x for x in BotData["owners"]]:
            code: str = "".join("    "+x+"\n" for x in ctx.message.content.split('```')[1].split("\n"))

            global_vars: dict = {"self" : self, "ctx" : ctx, "discord" : discord, "asyncio" : asyncio}
            async_code: str = f"""async def run():
  try:
    {code}  
  except Exception as error:
    print(type(error).__name__+\":\"+str(error))
                 
asyncio.create_task(run())"""
                 
            normal_code: str = f"""def run():
  try:
     {code}
  except Exception as error:
    print(type(error).__name__+\":\"+str(error))
            
run()"""
                 
            code_to_execute: str = async_code if "await" in code else normal_code

            output: str = execute_python_code(code_to_execute)
            if not output:
                await ctx.send(content="```No data returned.```")
            else:  
                for msg in output:
                    for cut in [msg[i:i+1700 ] for i in range(0, len(msg), 17000)]:
                        if cut.strip() != "":
                            await ctx.send(content=f"```{cut}```")

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(ExecuteCommandOwner(bot))
