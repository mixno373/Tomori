import logging
import discord
from datetime import datetime, date
from cogs.const import *
from config.constants import *

logg = logging.getLogger('locale')
logg.setLevel(logging.DEBUG)
now = datetime.now()
logname = 'logs/locale-{}_{}.log'.format(now.day, now.month)
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
logg.addHandler(handler)

global locale
locale = {}
_conn = None
_client = None

async def init_locale(conn, client):
    _conn = conn
    _client = client
    columnNames = await conn.fetch("SELECT column_name FROM information_schema.columns WHERE table_name = 'locale'")
    columns = ""
    for column in columnNames:
        columns += "{}, ".format(column[0])
    fromBase = await conn.fetch("SELECT {} FROM locale".format(columns[:-2]))
    _locales = columnNames
    for name, *columns in fromBase:
        for index, column in enumerate(columns):
            if not columnNames[index+1][0] in locale.keys():
                locale[columnNames[index+1][0]] = {}
            locale[columnNames[index+1][0]].setdefault(name, column)

async def is_lang_exists(lang, key):
    if lang in locale.keys() and key in locale[lang].keys():
        logg.info("Pizdato locale key - '{}', '{}'".format(lang, key))
        return True
    else:
        logg.info("Missing locale key - '{}', '{}'".format(lang, key))
        return False

async def get_localized(lang, key):
    logg.info("Hueta - '{}', '{}'".format(lang, key))
    if await is_lang_exists(lang, key): return locale[lang][key]
    return "hueta"

async def get_default_embed_message(lang, message):
    em = discord.Embed(colour=default_color)
    em.set_footer(text=await get_localized(lang, "global_time_response").format(int((datetime.utcnow() - message.timestamp).microseconds / 1000)))
    return em

async def get_footer(lang, message):
    return await get_localized(lang, "global_time_response").format(int((datetime.utcnow() - message.timestamp).microseconds / 1000))

async def get_server_locale(server_id):
    return await _conn.fetchval("SELECT locale FROM settings WHERE discord_id={}".format(server_id))

async def send_command_error(message, lang):
    em = discord.Embed(description=await get_localized(lang, "global_not_available").format(message.author.mention), colour=error_color)
    em.set_footer(text=await get_localized(lang, "global_time_response").format(int((datetime.utcnow() - message.timestamp).microseconds / 1000)))
    await _client.send_message(message.channel, embed=em)
