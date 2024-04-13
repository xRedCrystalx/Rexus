import discord, sys, datetime
sys.dont_write_bytecode = True

class buttonHandler(discord.ui.View):
    """
    Button Handler for `discord.Button`s
    - timeout: `float` | `None` = `None`
    
    Functions:
    - `create_buttons()`
    - `paginator()`
    """
    def __init__(self, timeout: float | None = None) -> None:
        super().__init__(timeout=timeout)
        self.original_message: discord.InteractionMessage | None = None
        self.msgList: list = None
        self.currentPage: int = -1
        self.timeout: float | None = timeout
        

    def create_buttons(self, buttons: list[dict]) -> None:
        """
        Appends Buttons to `discord.Message` or `discord.Embed`
        - buttons: `list[dict]`
        
        Dictionary data:
        - label: `str`,
        - style: `discord.ButtonStyle`,
        - custom_id: `str`,
        - disabled: `bool`,
        - url: `str`,
        - emoji: `str` | `discord.Emoji` | `discord.PartialEmoji`,
        - row: `int`
        """
        def valiade_button(buttonData: dict) -> dict:
            config: dict = {
                "label" : str,
                "style" : discord.ButtonStyle,
                "custom_id" : str,
                "disabled" : bool,
                "url" : str,
                "emoji" : str | discord.Emoji | discord.PartialEmoji,
                "row" : int
            }
            for key in config:
                if buttonData.get(key) is not None:
                    if isinstance(buttonData[key], config[key]) is False:
                        buttonData[key] = None
                else:
                    buttonData[key] = False if key == "disabled" else discord.ButtonStyle.blurple if key == "style" else None
            return buttonData

        for button in buttons:
            button: dict = valiade_button(buttonData=button)
            try:
                self.add_item(discord.ui.Button(label=button["label"], style=button["style"], custom_id=button["custom_id"], disabled=button["disabled"], url=button["url"], emoji=button["emoji"], row=button["row"]))
            except Exception as error:
                print(f"Failed to create button with custom ID: {button['custom_id']}. {type(error).__name__}: {error}")
        return self

    def create_paginator(self, messages: list[str|discord.Embed]) -> None:
        """
        Creates paginator for `discord.Message` or `discord.Embed`
        - messages: `list[discord.Message|discord.Embed]`
        """
        self.msgList = messages
        self.add_item(discord.ui.Button(label="◄", custom_id=f"PAGINATOR:BACK", style=discord.ButtonStyle.blurple))
        self.add_item(discord.ui.Button(label="►", custom_id=f"PAGINATOR:NEXT", style=discord.ButtonStyle.blurple))
        self.add_item(discord.ui.Button(label="✕", custom_id=f"PAGINATOR:STOP", style=discord.ButtonStyle.red))  
        return self      
    
    async def paginator(self, value: int | bool, interaction: discord.Interaction) -> None:
        self.lenList: int = len(self.msgList)-1
        index: int = 0 if self.currentPage + value > self.lenList else self.lenList if self.currentPage + value < 0 else self.currentPage + value
        self.currentPage = index
        if value is False:
            await self.original_message.edit(view=None)
        else:
            if isinstance(self.msgList[index], str):
                await interaction.response.edit_message(content=f"{self.msgList[index]}\n\nPage {self.currentPage+1}/{self.lenList+1}")
            elif isinstance(self.msgList[index], discord.Embed):
                embed: discord.Embed = self.msgList[index]
                embed.set_footer(text=f"Page {self.currentPage+1}/{self.lenList+1}")
                embed.timestamp = datetime.datetime.now()
                await interaction.response.edit_message(embed=embed)
            else:
                print(f"An error has occured. Could not find str or discord.Embed object in list. Index: {index}")
        return None
            

    async def on_timeout(self) -> None:
        if self.original_message is not None:
            try:
                await self.original_message.edit(view=None)
            except:
                pass
        return None

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        custom_id: str = dict(interaction.data).get('custom_id')
        if interaction.type == discord.InteractionType.component and custom_id.startswith("PAGINATOR:"):
            await self.paginator(value=1 if custom_id.endswith(":NEXT") else -1 if custom_id.endswith(":BACK") else False, interaction=interaction)
        return None
    
    async def on_error(self, interaction: discord.Interaction, error: Exception, item: discord.ui.item.Item) -> None:
        return await super().on_error(interaction, error, item)