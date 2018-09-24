import discord
import asyncio
import requests
import logging
import time
from datetime import datetime, date
import string
import random
import copy
import json
import asyncpg
import copy
from flask import Flask, request
from discord.ext import commands
from discord.ext.commands import Bot
from config.settings import settings
from cogs.const import *
from cogs.locale import *


__name__ = "Tomori-webhooks"
__version__ = "3.20.0"

logger = logging.getLogger('webhooks')
logger.setLevel(logging.DEBUG)
now = datetime.now()
logname = 'logs/webhooks/{}_{}.log'.format(now.day, now.month)
try:
    f = open(logname, 'r')
except:
    f = open(logname, 'w')
    f.close()
finally:
    handler = logging.FileHandler(
        filename=logname,
        encoding='utf-8',
        mode='a')
handler.setFormatter(logging.Formatter(
    '%(asctime)s:%(levelname)s:%(name)s: %(message)s\n'))
logger.addHandler(handler)

client = Bot(command_prefix='!', shard_count=10)
client.remove_command('help')

loop = asyncio.get_event_loop()

global conn
conn = None

async def run_base():
    global conn
    try:
        conn = await asyncpg.create_pool(dsn="postgres://{user}:{password}@{host}:5432/{database}".format(host="localhost", database="tomori", user=settings["base_user"], password=settings["base_password"]), command_timeout=60)
    except:
        logger.error('PostgreSQL doesn\'t load.\n')
        exit(0)
    await init_locale(conn, client)

loop.run_until_complete(run_base())


async def init_app(loop):
    app = web.Application(loop=loop, middlewares=[])
    app.router.add_post('/api/v1', handler)
    return app

app = loop.run_until_complete(init_app(loop))
web.run_app(app, host='51.38.113.96', port=23456)


@client.event
async def on_ready():
    logger.info("Logged in as | who - {} | id - {}".format(clear_name(client.user.display_name), client.user.id))
    app.run()


client.run(settings["token"])
