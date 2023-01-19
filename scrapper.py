import asyncio
import getopt
import logging
import os
import sys

import discord
from discord.utils import setup_logging

from scrapper import ScrapperBot, HumbleScrapper
from scrapper.database import initialize_database, db
from scrapper.tools import Config

logger = logging.getLogger('ScrapperBotLogger')
logger.setLevel(logging.DEBUG)
consoleHandler = logging.StreamHandler()
consoleHandler.setLevel(logging.DEBUG)
logger.addHandler(consoleHandler)

logger2 = logging.getLogger('discord')
logger2.setLevel(logging.INFO)
logging.getLogger('discord.http').setLevel(logging.INFO)
logger2.addHandler(consoleHandler)


description = '''A Humble Bundle Choice Scraper'''

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

settings = Config.from_file_path()
bot = ScrapperBot(command_prefix='?', description=description, intents=intents, settings=settings)


'''@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('-----')'''


async def load_extensions():
    for name in os.listdir('./cogs'):
        if name.endswith('.py'):
            await bot.load_extension(f'cogs.{name[:-3]}')


async def main():
    opts, args = getopt.getopt(sys.argv[1:], 'sr', ['scrape', 'run'])
    run_bot = False
    for opt, arg in opts:
        if opt in ['-s', '--scrape']:
            initialize_database()
            scrapper = HumbleScrapper()
            r = await scrapper.initial_scrape()
            await scrapper.session.close()
            with db.atomic():
                [x.save() for x in r]
        elif opt in ['-r', '--run']:
            run_bot = True
    if not run_bot:
        await asyncio.sleep(0.1)
        return
    async with bot:
        if not bot.settings.token:
            print('Token not found, please fill out config.json.')
            sys.exit()
        setup_logging()
        await load_extensions()
        await bot.start(bot.settings.token)
        await asyncio.sleep(0.1)
    await asyncio.sleep(0.1)

asyncio.run(main())
