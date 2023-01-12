from typing import TYPE_CHECKING, Optional

import discord
from discord import app_commands
from discord.ext import commands
from fast_autocomplete import AutoComplete

if TYPE_CHECKING:
    from scrapper import ScraperBot


class TopicCog(commands.Cog):
    def __init__(self, bot: 'ScraperBot'):
        self.bot = bot

    @app_commands.command(name='search', description='Search for a Humble Choice Game')
    async def search(
            self,
            interaction: discord.Interaction,
            name: str
    ):
        ...

    @search.autocomplete('name')
    async def name_autocomplete(self, interaction: discord.Interaction, current: str):
        names = []
        autocomplete = AutoComplete(names)
        results = autocomplete.search(current, max_cost=3, size=25)
        return [
            app_commands.Choice(name=x, value=x)
            for x in results
        ]


async def setup(bot: 'ScraperBot'):
    await bot.add_cog(TopicCog(bot))
