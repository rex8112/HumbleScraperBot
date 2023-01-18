from typing import TYPE_CHECKING, Optional

import discord
from discord import app_commands
from discord.ext import commands
from fast_autocomplete import AutoComplete
from scrapper import HumbleChoiceMonth, HumbleScrapper, HumbleChoiceGame

if TYPE_CHECKING:
    from scrapper import ScrapperBot


class HumbleCog(commands.Cog):
    def __init__(self, bot: 'ScrapperBot'):
        self.bot = bot
        self.scraper = HumbleScrapper()
        self.months: dict[str, 'HumbleChoiceMonth'] = {}
        self.game_index: dict[str, 'HumbleChoiceGame'] = {}
        self.autocomplete = None

    async def cog_load(self) -> None:
        self.months = HumbleChoiceMonth.get_all()
        self.rebuild_autocomplete()

    def rebuild_autocomplete(self):
        game_index = {}
        for month in self.months.values():
            game_index.update(**month.games)
        self.game_index = game_index
        ac_names = {}
        for name in self.game_index.keys():
            ac_names[name] = {}
        self.autocomplete = AutoComplete(ac_names)

    @app_commands.command(name='search', description='Search for a Humble Choice Game')
    async def search(
            self,
            interaction: discord.Interaction,
            name: str
    ):
        game = self.game_index.get(name)
        if game:
            await interaction.response.send_message(**game.message_payload)
        else:
            await interaction.response.send_message('Not Found')

    @search.autocomplete('name')
    async def name_autocomplete(self, interaction: discord.Interaction, current: str):
        results = self.autocomplete.search(current, max_cost=3, size=25)
        return [
            app_commands.Choice(name=x[0], value=x[0])
            for x in results
        ]


async def setup(bot: 'ScrapperBot'):
    await bot.add_cog(HumbleCog(bot))
