from typing import TYPE_CHECKING

import discord
from discord.ui import *

if TYPE_CHECKING:
    from .humble_choice import HumbleChoiceMonth, HumbleChoiceGame


class HumbleSearchView(View):
    def __init__(self, search: str, results: list['HumbleChoiceGame']):
        self.search = search
        self.results = results
        super().__init__(timeout=60)
        self.select_game.options = [
            discord.SelectOption(label=x.name, value=str(i)) for i, x in enumerate(self.results)]

    @select(placeholder='Select Game for Details')
    async def select_game(self, interaction: discord.Interaction, sel: Select):
        index = int(sel.values[0])
        selected_game = self.results[index]
        await interaction.response.send(**selected_game.message_payload)


class HumbleGameView(View):
    def __init__(self, game: 'HumbleChoiceGame'):
        self.game = game
        l_button = Button(style=discord.ButtonStyle.url, label='Link', url=self.game.month.url, row=1)
        super().__init__(timeout=60)
        self.add_item(l_button)

