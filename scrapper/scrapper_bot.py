import logging
from typing import Optional

import discord
from discord.ext import commands

from .humble_scrapper import HumbleScrapper
from .humble_choice import HumbleChoiceMonth
from .tools import Config

logger = logging.getLogger('HeliosLogger')


class ScrapperBot(commands.Bot):
    def __init__(self, command_prefix, *, intents, settings: Config, **options):
        self.settings = settings
        self.ready_once = True

        super().__init__(command_prefix, intents=intents, **options)

    async def setup_hook(self) -> None:
        self.tree.on_error = self.on_slash_error

    async def on_ready(self):
        logger.info(f'Logged in as {self.user} (ID: {self.user.id})')
        if self.ready_once:
            ...

    @staticmethod
    async def on_slash_error(
            interaction: discord.Interaction,
            error: discord.app_commands.AppCommandError
    ):
        if interaction.response.is_done():
            await interaction.followup.send(f'Something went wrong\n```{type(error)}: {error}```')
        else:
            await interaction.response.send_message(f'Something went wrong\n```{type(error)}: {error}```')
