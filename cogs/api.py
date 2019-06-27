import discord
import asyncio
import requests
import time
from datetime import datetime, date
import string
import random
import copy
import json
import asyncpg
import pyshiki
from google import google
from discord.ext import commands
from config.settings import settings
from cogs.const import *
from cogs.locale import *
from config.constants import *


# shikimori = pyshiki.Api(settings["shiki_username"], settings["shiki_password"])
# shiki_url = "https://shikimori.org"

shiki_kinds = {
"tv":"Сериал",
"movie":"Фильм",
"ova":"OVA",
"ona":"ONA",
"special":"Спешл",
"music":"Клип"
}

shiki_statuses = {
"released":"Завершен",
"anons":"Анонсировано",
"ongoing":"Выходит",
"latest":"Недавнее"
}

async def api_shiki(client, conn, logger, context, name):
    message = context.message
    server_id = message.server.id
    const = await get_cached_server(conn, server_id)
    lang = const["locale"]
    if not lang in locale.keys():
        em = discord.Embed(description="{who}, {response}.".format(
            who=message.author.display_name+"#"+message.author.discriminator,
            response="ошибка локализации",
            colour=0xC5934B))
        await client.send_message(message.channel, embed=em)
        return
    em = discord.Embed(colour=int(const["em_color"], 16) + 512)
    if not const:
        em.description = locale[lang]["global_not_available"].format(who=message.author.display_name+"#"+message.author.discriminator)
        await client.send_message(message.channel, embed=em)
        return
    try:
        await client.delete_message(message)
    except:
        pass
    anime = shikimori.animes("search", q=name, limit=1).get()
    logger.info("shikimori = {anime}".format(anime=anime))
    if not anime:
        em.description = locale[lang]["api_anime_not_found"].format(
            who=message.author.display_name+"#"+message.author.discriminator,
            anime=name
        )
        await client.send_message(message.channel, embed=em)
        return
    em.set_footer(text="{name}#{discriminator}".format(
        name=message.author.name,
        discriminator=message.author.discriminator
    ))
    anime = anime[0]
    em.title=anime["name"]
    em.url=shiki_url+anime["url"]
    em.set_thumbnail(url=shiki_url+anime["image"]["original"])
    em.add_field(
        name="Название",
        value=anime["russian"],
        inline=True
    )
    kind = anime["kind"]
    if kind in shiki_kinds.keys():
        kind = shiki_kinds[kind]
    em.add_field(
        name="Тип",
        value=kind,
        inline=True
    )
    status = anime["status"]
    if status in shiki_statuses.keys():
        status = shiki_statuses[status]
    em.add_field(
        name="Статус",
        value=status,
        inline=True
    )
    em.add_field(
        name="Серии",
        value="{count} из {all}".format(
            count=anime["episodes_aired"],
            all=anime["episodes"]
        ),
        inline=True
    )
    await client.send_message(message.channel, embed=em)


async def api_google_search(client, conn, logger, context, name):
    message = context.message
    server_id = message.server.id
    const = await get_cached_server(conn, server_id)
    lang = const["locale"]
    if not lang in locale.keys():
        em = discord.Embed(description="{who}, {response}.".format(
            who=message.author.display_name+"#"+message.author.discriminator,
            response="ошибка локализации",
            colour=0xC5934B))
        await client.send_message(message.channel, embed=em)
        return
    em = discord.Embed(colour=int(const["em_color"], 16) + 512)
    try:
        await client.delete_message(message)
    except:
        pass
    dat = google.search(name, 1)
    if not dat:
        em.description = locale[lang]["api_data_not_found"].format(
            who=message.author.display_name+"#"+message.author.discriminator,
            data=name
        )
        await client.send_message(message.channel, embed=em)
        return
    logg.info("google = {data}".format(data=str(dat)))
    em.set_footer(text="{name}#{discriminator}".format(
        name=message.author.name,
        discriminator=message.author.discriminator
    ))
    em.add_field(
        name="Response",
        value=str(dat),
        inline=True
    )
    await client.send_message(message.channel, embed=em)
