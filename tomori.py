import sys
import discord
import asyncio
import aiohttp
from io import BytesIO
from typing import Union
from aiohttp import ClientSession
import requests
import logging
import time
from datetime import datetime, date
import string
import random
import copy
import apiai, json
import asyncpg
import dbl
from discord.ext import commands
from discord.ext.commands import Bot
from config.settings import settings
from cogs.const import *
from cogs.economy import *
from cogs.fun import *
from cogs.admin import *
from cogs.other import *
from cogs.util import *
from cogs.locale import *
from cogs.guilds import *
# from cogs.api import *
from cogs.ids import *
from cogs.discord_hooks import Webhook
from config.constants import *


__name__ = "Tomori"
__version__ = "4.29.0"
SHARD_ID = int(sys.argv[1])
SHARD_COUNT = int(sys.argv[2])


logger = logging.getLogger('tomori')
logger.setLevel(logging.DEBUG)
now = datetime.utcnow()
logname = 'logs/shard{}_{}_{}.log'.format(SHARD_ID-1, now.day, now.month)
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
    '%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

loggers = logging.getLogger('tomori-inform')
loggers.setLevel(logging.DEBUG)
now = datetime.utcnow()
logname = 'logs/inform->shard{}_{}_{}.log'.format(SHARD_ID-1, now.day, now.month)
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
    '%(message)s'))
loggers.addHandler(handler)

dlogger = logging.getLogger('tomori-ddos')
dlogger.setLevel(logging.DEBUG)
now = datetime.utcnow()
logname = 'logs/ddos/shard{}_{}_{}.log'.format(SHARD_ID-1, now.day, now.month)
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
    '%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
dlogger.addHandler(handler)


loop = asyncio.get_event_loop()

global conn
conn = None
global client
client = None
global dblpy
dblpy = None
async def get_prefixes():
    global client
    client = Bot(command_prefix=prefix_list, shard_id=SHARD_ID-1, shard_count=SHARD_COUNT, cache_auth=False, max_messages=3000)
    client.remove_command('help')

async def run_base():
    global conn
    try:
        conn = await asyncpg.create_pool(dsn="postgres://{user}:{password}@{host}:5432/{database}".format(host="localhost", database="tomori", user=settings["base_user"], password=settings["base_password"]), command_timeout=60)
        muted = await conn.fetch("SELECT * FROM mods WHERE type = 'muted_users' AND server_id <> '485400595235340303' ORDER BY condition::bigint ASC")
        if muted:
            for user in muted:
                add_muted(client, user)
    except:
        logger.error('PostgreSQL doesn\'t load.\n')
        exit(0)
    await init_locale(conn, client)


loop.run_until_complete(get_prefixes())
loop.run_until_complete(run_base())




headers = {'authorization': "Bot "+settings["token"], 'Content-Type': 'application/json'}
discord_api_url = "https://discordapp.com/api/v6"

rq = requests.session()
headers = rq.headers
headers.update({'authorization': "Bot "+settings["token"], 'Content-Type': 'application/json'})



def is_it_admin():
    def predicate(ctx):
        if ctx.message.author == ctx.message.server.owner:
            return True
        return any(role.permissions.administrator for role in ctx.message.author.roles)
    return commands.check(predicate)

def is_it_owner():
    def predicate(ctx):
        return True if ctx.message.author == ctx.message.server.owner else False
    return commands.check(predicate)

def is_it_admin_or_dev():
    def predicate(ctx):
        if ctx.message.author.id in admin_list:
            return True
        if ctx.message.author == ctx.message.server.owner:
            return True
        return any(role.permissions.administrator for role in ctx.message.author.roles)
    return commands.check(predicate)

def is_it_me():
    def predicate(ctx):
        return ctx.message.author.id in admin_list
    return commands.check(predicate)

def is_it_support():
    def predicate(ctx):
        if ctx.message.author.id in admin_list:
            return True
        return ctx.message.author.id in support_list
    return commands.check(predicate)




async def working():
    if not SHARD_ID == 1:
        return
    await client.wait_until_ready()
    while not client.is_closed:
        now = int(time.time())
        begin_time = datetime.utcnow()
        workCooldownNow = now - WORK_COOLDOWN
        servers = await conn.fetch("SELECT discord_id, work_count FROM settings WHERE is_work = True")

        if not servers:
            await asyncio.sleep(WORK_DELAY)
            continue

        for discordId, workCount in servers:
            await conn.execute("UPDATE users SET work_time = 0, cash = cash + {workCount} WHERE work_time > 0 AND work_time <= {workCooldown}".format(
                workCount=workCount,
                workCooldown=workCooldownNow
            ))

        logger.info("working time = {}ms\n".format(int((datetime.utcnow() - begin_time).microseconds / 1000)))
        await asyncio.sleep(WORK_DELAY)



async def statuses():
    await client.wait_until_ready()
    while not client.is_closed:
        await client.change_presence(game=discord.Game(type=1, url="https://www.twitch.tv/tomori_bot", name="https://www.twitch.tv/tomori_bot"))

        servers_count = len(client.servers)
        users_count = 0
        try:
            for server in client.servers:
                users_count += server.member_count
        except:
            pass
        count = str(users_count)
        if int(users_count/1000000) > 0:
            count = str(int(users_count/1000000))+"M"
        elif int(users_count/1000) > 0:
            count = str(int(users_count/1000))+"K"
        msg = Webhook(
            web_url=wh_log_url["shards"],
            color=3553599,
            description="SHARD #{} | Servers {} | Users {}".format(SHARD_ID, servers_count, count)
        )
        await msg.post()

        await asyncio.sleep(600)



async def mutting():
    global muted_users
    await client.wait_until_ready()
    while True:
        if muted_users:
            t = int(time.time())
            min_t = min(muted_users.keys())
            if t >= min_t:
                objs = muted_users.pop(min_t)
                for o in objs:
                    if o["type"] == "unmute":
                        await u_unmute(client, conn, o["server"], o["member"])
                await asyncio.sleep(60)
            else:
                await asyncio.sleep(10)
        else:
            await asyncio.sleep(10)

async def reset_nitro():
    if not SHARD_ID == 1:
        return
    await client.wait_until_ready()
    while True:
        dat = await conn.fetch("SELECT * FROM mods WHERE type='reset_badge' AND condition::bigint < {time} AND condition::bigint > 10".format(time=int(time.time())))
        if dat:
            for user in dat:
                await asyncio.wait([
                    remove_badges(conn, user["name"], [user["value"]]),
                    conn.execute("DELETE FROM mods WHERE id={id}".format(id=user["id"]))
                ])
        await asyncio.sleep(300)


async def dbl_updating():
    await client.wait_until_ready()
    dblpy = dbl.Client(client, settings["dbl_token"])
    while True:
        try:
            await dblpy.post_guild_count()
        except:
            pass
        await asyncio.sleep(1800)




@client.event
async def on_member_ban(member):
    if member.server.id in not_log_servers:
        return
    await tomori_log_ban(client, member, SHARD_ID)

@client.event
async def on_member_unban(server, user):
    if user.server.id in not_log_servers:
        return
    await tomori_log_unban(client, server, user, SHARD_ID)






@client.event
async def on_server_join(server):
    logger.info("Joined at server - {} | id - {}\n".format(server.name, server.id))
    dat = await conn.fetchrow("SELECT name FROM settings WHERE discord_id = '{}'".format(server.id))
    if not dat:
        lang = "russian"
        if not server.region == "russia":
            lang = "english"
        await conn.execute("INSERT INTO settings(name, discord_id, locale) VALUES('{name}', '{discord_id}', '{locale}')".format(name=clear_name(server.name[:50]), discord_id=server.id, locale=lang))

    members_all = [1 if not member.bot else 0 for member in server.members].count(1)
    members_online = members_all - [1 if member.status == discord.Status.offline and not member.bot else 0 for member in server.members].count(1)
    owner = server.owner if server.owner else client.user
    payload = {
        "title": "🔵 New server join",
        "username": server.name+" | "+server.id,
        "avatar_url": (server.icon_url if server.icon_url else client.user.default_avatar_url).rsplit(".", maxsplit=1)[0]+".png",
        "color": 3553599,
        "footer": {
            "text": owner.name+"#"+owner.discriminator+" | "+owner.id,
            "icon_url": owner.avatar_url if owner.avatar_url else client.user.default_avatar_url
        },
        "fields": [
            {
                "name": "Members",
                "value": "<:online:582637296344367105>{on}\xa0<:all:582637296105422853>{all}".format(
                    on=members_online,
                    all=members_all
                ),
                "inline": True
            }
        ]
    }
    msg = Webhook(web_url=wh_log_url["servers"], **payload)
    await msg.post()

@client.event
async def on_server_remove(server):
    logger.info("Removed from server - {} | id - {}\n".format(server.name, server.id))

    payload = {
        "title": "🔴 Server removed",
        "username": server.name+" | "+server.id,
        "avatar_url": (server.icon_url if server.icon_url else client.user.default_avatar_url).rsplit(".", maxsplit=1)[0]+".png",
        "color": 3553599,
        "fields": [
            {
                "name": "Members",
                "value": server.member_count,
                "inline": True
            }
        ]
    }
    msg = Webhook(web_url=wh_log_url["servers"], **payload)
    await msg.post()


global voice_clients
voice_clients = {}

spam_message = []

async def spaming():
    await client.wait_until_ready()
    global spam_message
    while True:
        spam_message = []
        await asyncio.sleep(10)

@client.event
async def on_voice_state_update(before, after):
    if before.server.id in not_log_servers:
        return
    ret = '---------[voice_state_update]:{0.server.name} | {0.server.id}\n'.format(before)
    if before.voice.voice_channel:
        ret += 'before - {0.name} | {0.id} -> {0.voice.voice_channel.name} | {0.voice.voice_channel.id}\n'.format(before)
    if after.voice.voice_channel:
        ret += 'after - {0.name} | {0.id} -> {0.voice.voice_channel.name} | {0.voice.voice_channel.id}\n'.format(after)
    logger.info(ret)
    if before.bot:
        if before.voice.voice_channel and len(before.voice.voice_channel.voice_members) == 0:
            const = await get_cached_server(conn, before.server.id)
            await check_empty_voice(client, conn, const, before, before.voice.voice_channel)
        return
    global voice_clients
    const = await get_cached_server(conn, before.server.id)
    if not const:
        logger.error("'const' doesn't exists((")
        return
    if before.voice.voice_channel:
        if (not after.voice.voice_channel or (after.server.afk_channel and after.server.afk_channel.id == after.voice.voice_channel.id)) and before.id in voice_clients.keys():
            voice_time = int(time.time()) - voice_clients.pop(before.id, int(time.time()))
            if not const["is_global"]:
                stats_type = before.server.id
            else:
                stats_type = "global"
            dat = await conn.fetchrow("UPDATE users SET voice_time = voice_time + {time} WHERE discord_id = '{id}' AND stats_type = '{stats_type}' RETURNING voice_time".format(
                time=voice_time,
                id=before.id,
                stats_type=stats_type
            ))
            if dat:
                new_voice_time = dat["voice_time"]
                await u_check_voice_time(client, conn, const, before, voice_time, new_voice_time)
        await check_empty_voice(client, conn, const, before, before.voice.voice_channel)
    if after.voice.voice_channel:
        if not before.id in voice_clients.keys() and not (after.server.afk_channel and after.server.afk_channel.id == after.voice.voice_channel.id):
            voice_clients[before.id] = int(time.time())
        global spam_message
        if before.id in spam_message:
            return
        spam_message.append(before.id)
        if const["create_lobby_id"] and const["create_lobby_category_id"] and after.voice.voice_channel.id == const["create_lobby_id"]:
            voice_clients.pop(after.id)
            #if await check_captcha(client, conn, const, after, after): #client.get_channel("484805058760933377")
            payload = {
                "name": after.display_name,
                "type": 2,
                "user_limit": const["create_lobby_user_limit"],
                "parent_id": const["create_lobby_category_id"],
                "permission_overwrites": [
                    {
                        "id": after.server.default_role.id,
                        "type": "role",
                        "allow": const["create_lobby_everyone_permissions"],
                        "deny": 0
                    },
                    {
                        "id": after.id,
                        "type": "member",
                        "allow": const["create_lobby_owner_permissions"],
                        "deny": 0
                    }
                ]
            }
            response = rq.post("{base}/guilds/{server}/channels".format(base=discord_api_url, server=after.server.id), json=payload, headers=headers)
            response = json.loads(response.text)
            if response.get("id"):
                payload = {
                    "channel_id": response.get("id")
                }
                rq.patch("{base}/guilds/{server}/members/{member}".format(base=discord_api_url, server=after.server.id, member=after.id), json=payload, headers=headers)


async def check_empty_voice(client, conn, const, member, channel):
    if member.server.id in not_log_servers:
        return
    response = rq.get("{base}/channels/{channel}".format(base=discord_api_url, channel=channel.id), headers=headers)
    response = json.loads(response.text)
    parent_id = response.get("parent_id")
    parent_channel = client.get_channel(parent_id)
    if parent_id:
        if parent_id == const["create_lobby_category_id"] and response.get("id") != const["create_lobby_id"] and len(channel.voice_members) == 0:
            try:
                await client.delete_channel(channel)
            except discord.errors.Forbidden:
                pass




@client.event
async def on_socket_raw_receive(raw_msg):
    if not isinstance(raw_msg, str):
        return
    msg = json.loads(raw_msg)
    type = msg.get("t")
    data = msg.get("d")
    if not data:
        return
    if type == "MESSAGE_REACTION_ADD":
        await u_reaction_add(client, conn, logger, data)
    if type == "MESSAGE_REACTION_REMOVE":
        await u_reaction_remove(client, conn, logger, data)






@client.event
async def on_member_update(before, after):
    if (before.server and before.server.id in not_log_servers) or (after.server and after.server.id in not_log_servers):
        return
    # STREAM NOTIFY
    if before.game != after.game and after.game and after.game.type == 1:
        data = await conn.fetchrow("SELECT * FROM mods WHERE server_id = '{server}' AND name = '{member}' AND type = 'stream_notification'".format(server=before.server.id, member=before.id))
        if data:
            channel = client.get_channel(data["condition"])
            if channel:
                name = ""
                url = ""
                if after.game.name:
                    name = after.game.name
                if after.game.url:
                    url = after.game.url
                await client.send_message(channel, data["value"].format(
                    name=name,
                    url=url
                ))




@client.event
async def on_member_join(member):
    if member.server.id in not_log_servers:
        return
    dlogger.info("{0.server.name} | {0.server.id} ({delta} дней) joined at server - {0.name}#{0.discriminator} | {0.id}".format(member, delta=(datetime.utcnow() - member.created_at).days))
    if member.server.id in not_log_servers:
        return

    global conn
    dat = await get_cached_server(conn, member.server.id)
    black = await conn.fetchrow("SELECT * FROM black_list_not_ddos WHERE discord_id = '{id}'".format(id=member.id))
    if black:
        lang = dat["locale"]
        if lang in locale.keys():
            if black["reason"]:
                reason = black["reason"]
            else:
                reason = locale[lang]["admin_no_reason"]
            c_ban = discord.Embed(colour=0xF10118)
            c_ban.set_author(name=locale[lang]["global_black_list_title"], icon_url=member.server.icon_url)
            c_ban.description = locale[lang]["global_black_list_desc"].format(who=member.display_name+"#"+member.discriminator+" ("+member.mention+")")
            c_ban.add_field(
                name=locale[lang]["admin_reason"],
                value=reason,
                inline=False
            )
            c_ban.set_footer(text="ID: {id}".format(
                id=member.id
            ))
            c_ban.timestamp = datetime.utcnow()
            for user in member.server.members:
                if any(role.permissions.administrator for role in user.roles) or user.id == member.server.owner.id:
                    try:
                        await client.send_message(user, embed=c_ban)
                    except:
                        pass

    await u_check_travelling(client, member)

    if member.server.id in welcome_responses_dm.keys():
        text, em = await dict_to_embed(welcome_responses_dm.get(member.server.id))
        try:
            await client.send_message(member, content=text, embed=em)
        except:
            pass

    roles = []

    pattern = "[A-Z][a-zA-Z]+[0-9]{2,4}"
    names = re.findall(pattern, member.name)
    if names:
        now = datetime.utcnow()
        if now - member.created_at < timedelta(days=7):
            try:
                role = discord.utils.get(member.server.roles, id=const["antispam_role_id"])
                if role:
                    roles.append(role)
            except:
                pass

    if dat:
        role = discord.utils.get(member.server.roles, id=dat["autorole_id"])
        if role:
            roles.append(role)
        role_dat = await conn.fetchrow("SELECT * FROM mods WHERE server_id = '{server}' AND name = '{member}' AND type = 'saved_roles'".format(server=member.server.id, member=member.id))
        if role_dat:
            role_ids = role_dat["arguments"]
            if role_ids:
                for role_id in role_ids:
                    role = discord.utils.get(member.server.roles, id=str(role_id))
                    if role:
                        roles.append(role)
    if roles:
        try:
            await client.replace_roles(member, *roles)
        except:
            pass

        welcome_channel = client.get_channel(dat["welcome_channel_id"])
        if welcome_channel:
            try:
                await send_welcome_pic(client, welcome_channel, member, dat)
            except:
                pass


@client.event
async def on_member_remove(member):
    if member.server.id in not_log_servers:
        return
    logger.info("{0.name} | {0.id} removed from server - {1.name} | {1.id}\n".format(member, member.server))
    dat = await conn.fetchrow("SELECT * FROM settings WHERE discord_id = '{}'".format(member.server.id))
    roles = []
    for role in member.roles:
        if role.position == 0:
            continue
        roles.append(role.id)
    if roles:
        roles = "', '".join(roles)
        role_dat = await conn.fetchrow("SELECT * FROM mods WHERE server_id = '{server}' AND name = '{member}' AND type = 'saved_roles'".format(server=member.server.id, member=member.id))
        if role_dat:
            await conn.execute("UPDATE mods SET arguments = ARRAY['{roles}'] WHERE server_id = '{server}' AND name = '{member}' AND type = 'saved_roles'".format(
                server=member.server.id,
                member=member.id,
                roles=roles
            ))
        else:
            await conn.execute("INSERT INTO mods(server_id, type, name, arguments) VALUES ('{server}', 'saved_roles', '{member}', ARRAY['{roles}'])".format(
                server=member.server.id,
                member=member.id,
                roles=roles
            ))
    if dat:
        welcome_channel = discord.utils.get(member.server.channels, id=dat["welcome_channel_id"])
        if welcome_channel and dat["welcome_leave_text"]:
            message = welcomer_format(dat["welcome_leave_text"], member)
            await client.send_message(welcome_channel, message)


@client.event
async def on_ready():
    await client.change_presence(game=discord.Game(type=0, name="tring to launch (^_^)"))
    client.loop.create_task(working())
    print('Logged in as')
    logger.info("Logged in as | who - {} | id - {}\n".format(clear_name(client.user.display_name), client.user.id))
    print(clear_name(client.user.display_name))
    print(client.user.id)
    print('------')
    client.loop.create_task(statuses())
    client.loop.create_task(reset_nitro())
    client.loop.create_task(dbl_updating())
    client.loop.create_task(mutting())
    client.loop.create_task(spaming())
    client.loop.create_task(clear_cache())
    print('Shard %s running' % str(SHARD_ID))

@client.event
async def on_command_error(error, ctx):
    if isinstance(error, commands.CommandOnCooldown):
        msg = await client.send_message(ctx.message.channel, "{who}, command is on cooldown. Wait {seconds} seconds".format(who=ctx.message.author.mention, seconds=int(error.retry_after)))
        try:
            await client.delete_message(ctx.message)
        except:
            pass
        await asyncio.sleep(5)
        try:
            await client.delete_message(msg)
        except:
            pass
    pass










# LEGASY CODE
@client.command(pass_context=True, name="enable", help="Активировать сервер.")
@commands.cooldown(1, 1, commands.BucketType.user)
async def enable(context):
    if not await is_it_has_badge(conn, client, True, context.message, "Staff"):
        return
    await a_enable(client, conn, context)

# LEGASY CODE
@client.command(pass_context=True, name="disable", help="Деактивировать сервер (Только для меня).")
@commands.cooldown(1, 1, commands.BucketType.user)
async def disable(context):
    if not await is_it_has_badge(conn, client, True, context.message, "Staff"):
        return
    await a_disable(client, conn, context)

@client.command(pass_context=True, name="timely", help="Cобрать печенюхи.")
@commands.cooldown(1, 1, commands.BucketType.user)
async def timely(context):
    await e_timely(client, conn, context)

@client.command(pass_context=True, name="work", help="Выйти на работу.")
@commands.cooldown(1, 1, commands.BucketType.user)
async def work(context):
    await e_work(client, conn, context)

@client.command(pass_context=True, name="help", aliases=['h', 'рудз'], hidden=True, help="Показать список команд.")
@commands.cooldown(1, 1, commands.BucketType.user)
async def helps(context):
    await o_help(client, conn, context)

@client.command(pass_context=True, name='server', hidden=True, help="Показать информацию о сервере.")
@commands.cooldown(1, 1, commands.BucketType.user)
async def server(context):
    await o_server(client, conn, context)

@client.command(pass_context=True, name='servers', hidden=True)
@commands.cooldown(1, 1, commands.BucketType.user)
async def servers(context, page: int=1):
    if not await is_it_has_badge(conn, client, True, context.message, "Staff"):
        return
    await o_servers(client, conn, context, page)

@client.command(pass_context=True, name="ping", help="Проверить задержку соединения.")
@commands.cooldown(1, 1, commands.BucketType.user)
async def ping(context):
    await o_ping(client, conn, context)

@client.command(pass_context=True, name="webhook", aliases=["wh"])
@commands.cooldown(1, 1, commands.BucketType.user)
async def webhook(context, name: str=None, *, value: str=None):
    await o_webhook(client, conn, context, name, value)

@client.command(pass_context=True, name="createvoice", help="Создать войс канал.")
@commands.cooldown(1, 1, commands.BucketType.user)
async def createvoice(context):
    if not await is_it_has_badge(conn, client, True, context.message, "Staff"):
        return
    message = context.message
    server_id = message.server.id
    who = message.author
    const = await conn.fetchrow("SELECT * FROM settings WHERE discord_id = '{}'".format(server_id))
    lang = const["locale"]
    if not lang in locale.keys():
        em = discord.Embed(description="{who}, {response}.".format(
            who=message.author.display_name+"#"+message.author.discriminator,
            response="ошибка локализации",
            colour=0xC5934B))
        await client.send_message(message.channel, embed=em)
        return
    if not const:
        em.description = locale[lang]["global_not_available"].format(who=message.author.display_name+"#"+message.author.discriminator)
        await client.send_message(message.channel, embed=em)
        return
    em = discord.Embed(colour=int(const["em_color"], 16) + 512)
    try:
        await client.delete_message(message)
    except:
        pass
    payload = {
        "name": "Tomori private voices",
        "type": 4
    }
    response = rq.post("{base}/guilds/{server}/channels".format(base=discord_api_url, server=server_id), json=payload, headers=headers)
    category_id = json.loads(response.text).get("id")
    payload = {
        "name": "Create voice [+]",
        "type": 2,
        "parent_id": category_id,
        "permission_overwrites": [
            {
                "id": message.server.default_role.id,
                "type": "role",
                "allow": const["create_lobby_public_permissions"],
                "deny": 0
            }
        ]
    }
    response = rq.post("{base}/guilds/{server}/channels".format(base=discord_api_url, server=server_id), json=payload, headers=headers)
    lobby_id = json.loads(response.text).get("id")
    await conn.execute("UPDATE settings SET create_lobby_id = '{lobby}', create_lobby_category_id = '{category}', is_createvoice = TRUE WHERE discord_id = '{server}'".format(
        lobby=lobby_id,
        category=category_id,
        server=server_id
    ))
    pop_cached_server(server_id)

# LEGASY CODE
@client.command(pass_context=True, name="region")
@commands.cooldown(1, 1, commands.BucketType.user)
async def region(context):
    if not await is_it_has_badge(conn, client, True, context.message, "Staff"):
        return
    await client.send_message(context.message.channel, context.message.server.region)

# LEGASY CODE
@client.command(pass_context=True, name="setvoice", help="Установить войс канал.")
@commands.cooldown(1, 1, commands.BucketType.user)
async def setvoice(context):
    await u_setvoice(client, conn, logger, context)

# LEGASY CODE
@client.command(pass_context=True, name="setlobby", help="Установить войс для ожидания.")
@commands.cooldown(1, 1, commands.BucketType.user)
async def setlobby(context):
    await u_setlobby(client, conn, logger, context)

@client.command(pass_context=True, name="buy", hidden=True, help="Купить роль.")
@commands.cooldown(1, 1, commands.BucketType.user)
async def buy(context, *, value: str):
    await e_buy(client, conn, context, value)

@client.command(pass_context=True, name="shop", help="Показать магазин ролей.")
@commands.cooldown(1, 1, commands.BucketType.user)
async def shop(context, page: int=None):
    await e_shop(client, conn, context, page)

@client.command(pass_context=True, name="lvlup", help="Показать список ролей за уровень.")
@commands.cooldown(1, 1, commands.BucketType.user)
async def lvlup(context, page: int=None):
    await o_lvlup(client, conn, context, page)

@client.command(pass_context=True, name="synclvlup", help="Синхронизировать уровни участников и роли за уровень.")
@commands.cooldown(1, 1, commands.BucketType.user)
async def synclvlup(context):
    if not await is_it_has_badge(conn, client, True, context.message, "Staff"):
        return
    await o_synclvlup(client, conn, context)

@client.command(pass_context=True, name="synclvl", help="Синхронизировать уровни участников и роли за уровень.")
@commands.cooldown(1, 1, commands.BucketType.user)
async def synclvlup(context):
    if not await is_it_has_badge(conn, client, True, context.message, "nitro"):
        return
    await o_synclvlup(client, conn, context)

# LEGASY CODE
@client.command(pass_context=True, name="captcha")
async def captcha(context):
    if not await is_it_has_badge(conn, client, True, context.message, "Staff"):
        return
    const = await get_cached_server(conn, context.message.server.id)
    if await check_captcha_new(client, conn, const, context.message.channel, context.message.author):
        await client.send_message(context.message.channel, "✅")

@client.command(pass_context=True, name="pay", help="Получить печенюхи из банка сервера.")
@commands.cooldown(1, 1, commands.BucketType.user)
@is_it_admin()
async def pay(context, count: str):
    await e_pay(client, conn, context, count)

@client.command(pass_context=True, name="send", help="Переслать файл от имени бота.")
@commands.cooldown(1, 15, commands.BucketType.user)
@is_it_admin()
async def _send(context, url: str):
    await a_send(client, conn, context, url)

@client.command(pass_context=True, name="say", hidden=True, help="Напишет ваш текст.")
@commands.cooldown(1, 1, commands.BucketType.user)
@is_it_admin()
async def say(context, *, value: str):
    await a_say(client, conn, context, value)

@client.command(pass_context=True, name="find_owner", aliases=["fo"], hidden=True)
@commands.cooldown(1, 30, commands.BucketType.user)
# @is_it_support()
async def find_owner(context, member_id: str):
    await a_find_owner(client, conn, context, member_id)

@client.command(pass_context=True, name="find_user", aliases=["fu"], hidden=True)
@commands.cooldown(1, 30, commands.BucketType.user)
# @is_it_support()
async def find_user(context, member_id: str):
    await a_find_user(client, conn, context, member_id)

@client.command(pass_context=True, name="find_voice", aliases=["fv"], hidden=True)
@commands.cooldown(1, 30, commands.BucketType.user)
# @is_it_support()
async def find_voice(context, member_id: str):
    await a_find_voice(client, conn, context, member_id)

@client.command(pass_context=True, name="sync", hidden=True)
@commands.cooldown(1, 1, commands.BucketType.user)
async def sync(context):
    if not await is_it_has_badge(conn, client, True, context.message, "Staff"):
        return
    await clear_caches()

@client.command(pass_context=True, name="sql", hidden=True, help="Запрос в базу.")
@commands.cooldown(1, 1, commands.BucketType.user)
@is_it_me()
async def _base(context, *, request: str):
    if not await is_it_has_badge(conn, client, True, context.message, "Staff"):
        return
    await a_base(client, conn, context, request)

@client.command(pass_context=True, name="verify", aliases=["v"], hidden=True)
async def verify(context, identify: str):
    if not await is_it_has_badge(conn, client, True, context.message, "Staff"):
        return
    await u_verify(client, conn, context, identify)

@client.command(pass_context=True, name="welcometest", hidden=True)
async def welcome(context):
    if not await is_it_has_badge(conn, client, True, context.message, "Staff"):
        return
    message = context.message
    const = await conn.fetchrow("SELECT * FROM settings WHERE discord_id = '{}'".format(message.server.id))
    await client.delete_message(message)
    await send_welcome_pic(client, message.channel, message.author, const)

@client.command(pass_context=True, name="invite_server", hidden=True, help="Создать инвайт на данный сервер.")
@commands.cooldown(1, 1, commands.BucketType.user)
async def invite_server(context, server_id: str=None):
    if not await is_it_has_badge(conn, client, True, context.message, "Staff"):
        return
    await u_invite_server(client, conn, context, server_id)

@client.command(pass_context=True, name="invite_channel", hidden=True, help="Создать инвайт на данный канал.")
@commands.cooldown(1, 1, commands.BucketType.user)
async def invite_channel(context, channel_id: str=None):
    if not await is_it_has_badge(conn, client, True, context.message, "Staff"):
        return
    await u_invite_channel(client, conn, context, channel_id)

# LEGASY CODE
@client.command(pass_context=True, name="report", help="Отправить репорт.")
@commands.cooldown(1, 300, commands.BucketType.user)
async def report(context, mes: str=None):
    await o_report(client, conn, context)

@client.command(pass_context=True, name="give", help="Передать свои печенюхи.")
@commands.cooldown(1, 1, commands.BucketType.user)
async def give(context, who: discord.Member, count: str):
    await e_give(client, conn, context, who, count)

@client.command(pass_context=True, name="take", help="Забрать печенюхи.")
@commands.cooldown(1, 1, commands.BucketType.user)
async def take(context, who: discord.Member, count: int):
    await a_take(client, conn, context, who, count)

@client.command(pass_context=True, name="gift")
@commands.cooldown(1, 1, commands.BucketType.user)
async def gift(context, count: int):
    await e_gift(client, conn, context, count)

@client.command(pass_context=True, name="top", help="Показать топ юзеров.")
@commands.cooldown(1, 1, commands.BucketType.user)
async def top(context, page: int=None):
    await f_top(client, conn, context, page, "xp")

@client.command(pass_context=True, name="money", help="Показать топ юзеров.")
@commands.cooldown(1, 1, commands.BucketType.user)
async def money(context, page: int=None):
    await f_top(client, conn, context, page, "money")

@client.command(pass_context=True, name="voice", help="Показать топ юзеров.")
@commands.cooldown(1, 1, commands.BucketType.user)
async def voice(context, page: int=None):
    await f_top(client, conn, context, page, "voice")

@client.command(pass_context=True, name="set", help="Настройка.")
@commands.cooldown(1, 1, commands.BucketType.user)
async def set(context, arg1: str=None, arg2: str=None, *, args: str=None):
    await o_set(client, conn, context, arg1, arg2, args)

@client.command(pass_context=True, name="remove", aliases=["rm"], help="Настройка.")
@commands.cooldown(1, 1, commands.BucketType.user)
async def remove(context, arg1: str=None, arg2: str=None, *, args: str=None):
    await o_remove(client, conn, context, arg1, arg2, args)

@client.command(pass_context=True, name="$", help="Посмотреть свой баланс.")
@commands.cooldown(1, 1, commands.BucketType.user)
async def cash(context):
    await e_cash(client, conn, context)

@client.command(pass_context=True, name="sex", help="Трахнуть.")
@commands.cooldown(1, 1, commands.BucketType.user)
async def sex(context, who: discord.Member):
    await f_sex(client, conn, context, who)

@client.command(pass_context=True, name="hug", help="Обнять.")
@commands.cooldown(1, 1, commands.BucketType.user)
async def hug(context, who: discord.Member):
    await f_hug(client, conn, context, who)

@client.command(pass_context=True, name="wink", help="Подмигнуть.")
@commands.cooldown(1, 1, commands.BucketType.user)
async def wink(context, who: discord.Member):
    await f_wink(client, conn, context, who)

@client.command(pass_context=True, name="five", help="Дать пять.")
@commands.cooldown(1, 1, commands.BucketType.user)
async def five(context, who: discord.Member):
    await f_five(client, conn, context, who)

@client.command(pass_context=True, name="fuck", help="Показать фак.")
@commands.cooldown(1, 1, commands.BucketType.user)
async def fuck(context, who: discord.Member):
    await f_fuck(client, conn, context, who)

@client.command(pass_context=True, name="punch", help="Дать леща.")
@commands.cooldown(1, 1, commands.BucketType.user)
async def punch(context, who: discord.Member):
    await f_punch(client, conn, context, who)

@client.command(pass_context=True, name="kiss", help="Поцеловать.")
@commands.cooldown(1, 1, commands.BucketType.user)
async def kiss(context, who: discord.Member):
    await f_kiss(client, conn, context, who)


@client.command(pass_context=True, name="ud", aliases=["urban"], help="Urban Dictionary.")
@commands.cooldown(1, 1, commands.BucketType.user)
async def urban_(context, *, text: str):
    await o_urban(client, conn, context, text)


@client.command(pass_context=True, name="drink", help="Уйти в запой.")
@commands.cooldown(1, 1, commands.BucketType.user)
async def drink(context):
    await f_drink(client, conn, context)

# LEGASY CODE
@client.command(pass_context=True, name="guild", help="Гильдии.")
@commands.cooldown(1, 1, commands.BucketType.user)
async def guild(context, category: str, arg1: str=None, *, args: str=None):
    await g_guild(client, conn, context, category, arg1, args)

@client.command(pass_context=True, name="roll", help="Зароллить число.")
@commands.cooldown(1, 1, commands.BucketType.user)
async def roll(context, one: int, two: int=0):
    await o_roll(client, conn, context, one, two)

@client.command(pass_context=True, name="br", help="Поставить деньги на рулетке.")
@commands.cooldown(1, 2, commands.BucketType.user)
async def br(context, count: str):
    await e_br(client, conn, context, count)

@client.command(pass_context=True, name="slots", aliases=["slot"], help="Поставить деньги на рулетке.")
@commands.cooldown(1, 2, commands.BucketType.user)
async def slots(context, count: str):
    await e_slots(client, conn, context, count)

# LEGASY CODE
@client.command(pass_context=True, name="rep", help="Выразить свое почтение.")
@commands.cooldown(1, 1, commands.BucketType.user)
async def rep(context, who: discord.Member):
    await f_rep(client, conn, context, who)

@client.command(pass_context=True, name="avatar", help="Показать аватар пользователя.")
@commands.cooldown(1, 1, commands.BucketType.user)
async def avatar(context, who: discord.Member=None):
    await o_avatar(client, conn, context, who)

@client.command(pass_context=True, name="me", aliases=["profile"], help="Вывести статистику пользователя картинкой.")
@commands.cooldown(1, 10, commands.BucketType.user)
async def me(context, who: discord.Member=None):
    await f_me(client, conn, context, who)

@client.command(pass_context=True, name="unfriend")
@commands.cooldown(1, 1, commands.BucketType.user)
async def unfriend(context, who_id: str, * , reason: str=None):
    if not await is_it_has_badge(conn, client, True, context.message, "Staff"):
        return
    await a_unfriend(client, conn, context, who_id, reason)

@client.command(pass_context=True, name="kick", help="Кикнуть пользователя.")
@commands.cooldown(1, 1, commands.BucketType.user)
async def kick(context, who: discord.Member, reason: str=None):
    await a_kick(client, conn, context, who, reason)

@client.command(pass_context=True, name="ban", help="Забанить пользователя.")
@commands.cooldown(1, 1, commands.BucketType.user)
async def ban(context, who: discord.Member, reason: str=None):
    await a_ban(client, conn, context, who, reason)

@client.command(pass_context=True, name="unban", help="Разбанить пользователя.")
@commands.cooldown(1, 1, commands.BucketType.user)
async def unban(context, *, name: str):
    await a_unban(client, conn, context, name)

@client.command(pass_context=True, name="mute", help="Замутить пользователя.")
@commands.cooldown(1, 1, commands.BucketType.user)
async def mute(context, who: str, reason: str=None):
    await a_mute(client, conn, context, who, reason)

@client.command(pass_context=True, name="unmute", help="Разамутить пользователя.")
@commands.cooldown(1, 1, commands.BucketType.user)
async def unmute(context, who: str, reason: str=None):
    await a_unmute(client, conn, context, who, reason)

@client.command(pass_context=True, name="start", help="Test.")
@commands.cooldown(1, 1, commands.BucketType.user)
@is_it_admin_or_dev()
async def start(context, channel_id: str, *, name: str=None):
    if not channel_id:
        return
    message = context.message
    em = discord.Embed(colour=0xC5934B)
    request_channel = client.get_channel(channel_id)
    if not request_channel:
        for server in client.servers:
            request_channel = server.get_member(channel_id)
            if request_channel:
                break
    if request_channel:
        if not message.author.id in admin_list and not request_channel in message.server.channels:
            em.description = "Соединение с каналом {name} не может быть установлено. Выберите любой канал на этом сервере".format(name=request_channel.name)
            await client.send_message(message.channel, embed=em)
            return
        if message.channel.is_private:
            chan_id = message.author.id
        else:
            chan_id = message.channel.id
        if not name:
            name="NULL"
        else:

            name = "'" + clear_name(name[:20]) + "'"
        dat = await conn.fetchrow("SELECT * FROM tickets WHERE request_id = '{request_id}'".format(request_id=request_channel.id))
        if not dat:
            await conn.execute("INSERT INTO tickets(request_id, response_id, name) VALUES('{request_id}', '{response_id}', {name})".format(request_id=request_channel.id, response_id=chan_id, name=name))
        else:
            await conn.execute("UPDATE tickets SET response_id = '{response_id}', name = {name} WHERE request_id = '{request_id}'".format(request_id=request_channel.id, response_id=chan_id, name=name))
        em.description = "Соединение с каналом {name} установлено".format(name=request_channel.name)
    else:
        em.description = "Соединение с каналом ID:{id} не было установлено. Проверьте ID канала".format(id=channel_id)
    await client.send_message(message.channel, embed=em)

@client.command(pass_context=True, name="stop", help="Test.")
@commands.cooldown(1, 1, commands.BucketType.user)
@is_it_admin_or_dev()
async def stop(context):
    message = context.message
    em = discord.Embed(colour=0xC5934B)
    if message.channel.is_private:
        chan_id = message.author.id
    else:
        chan_id = message.channel.id
    dat = await conn.fetchrow("SELECT * FROM tickets WHERE response_id = '{response_id}'".format(response_id=chan_id))
    if dat:
        em.description = "Соединение с каналом закрыто"
        try:
            await client.send_message(u_get_channel(client, dat["request_id"]), embed=em)
        except:
            pass
        await conn.execute("DELETE FROM tickets WHERE response_id = '{response_id}'".format(response_id=chan_id))
    else:
        em.description = "Нет активных соединений"
    try:
        await client.send_message(message.channel, embed=em)
    except:
        pass

@client.command(pass_context=True, name="clear", aliases=["cl"], hidden=True, help="Удалить последние сообщения.")
@commands.cooldown(1, 1, commands.BucketType.user)
async def clear(context, count: int=1, who: discord.Member=None):
    await a_clear(client, conn, context, count, who)

@client.command(pass_context=True, name="about", help="Показать информацию о боте.")
@commands.cooldown(1, 1, commands.BucketType.user)
async def about(context):
    await o_about(client, conn, context)

@client.command(pass_context=True, name="many", help="Выполнить несколько команд.")
@commands.cooldown(1, 1, commands.BucketType.user)
async def many(context):
    await o_many(client, conn, context)

@client.command(pass_context=True, name="invite", help="Получить ссылку на добавление бота себе на сервер.")
@commands.cooldown(1, 1, commands.BucketType.user)
async def invite(context):
    await o_invite(client, conn, context)

@client.command(pass_context=True, name="inv", help="Кастомный инвайт.")
@commands.cooldown(1, 10, commands.BucketType.user)
async def inv_(context, code: str, name: str=""):
    await o_inv(client, conn, context, code, name)




@client.event
async def on_message(message):
    if message.channel.is_private or message.server.id in not_log_servers or message.server.id in konoha_servers:
        message = None
        return
    await u_check_support(client, conn, logger, message)

    if not message.channel.is_private:
        pass
    else:
        await client.process_commands(message)
        return

    server_id = message.server.id
    serv = await get_cached_server(conn, server_id)
    if message.author.bot or not serv or not serv["is_enable"]:
        return


    if not serv["is_global"]:
        stats_type = message.server.id
    else:
        stats_type = "global"


    t = int(time.time())
    ava_url = message.author.avatar_url
    if not ava_url:
        ava_url = message.author.default_avatar_url
    ava_url = ava_url.rsplit(".", maxsplit=1)[0]+".png"
    dat = await conn.fetchrow("INSERT INTO users(name, discord_id, discriminator, xp_count, xp_time, messages, stats_type) \
VALUES('{name}', '{discord_id}', '{discriminator}', {count}, {time}, 1, '{stats_type}') \
ON CONFLICT ON CONSTRAINT global_local \
DO UPDATE SET xp_time={time}, xp_count=users.xp_count+{count}, cash=users.cash+{cash}, name='{name}', avatar_url='{ava_url}' \
WHERE users.stats_type='{stats_type}' AND users.discord_id='{discord_id}' AND users.xp_time<={time}-{cooldown} RETURNING *".format(
        stats_type=stats_type,
        time=t,
        cooldown=serv["xp_cooldown"],
        count=serv["xp_award_count"],
        cash=serv["message_award_count"],
        name=clear_name(message.author.display_name),
        discriminator=message.author.discriminator,
        discord_id=message.author.id,
        ava_url=ava_url
    ))
    try:
        if str(dat["xp_count"]+1) in xp_lvlup_list.keys():
            client.loop.create_task(u_check_lvlup(client, conn, message.channel, message.author, serv, str(dat["xp_count"]+1)))
    except:
        pass


    if message.content.startswith(serv["prefix"]) or message.content.startswith("!help"):
        if not message.channel.is_private and message.server.id == "548908334346928141":
            comm_name = message.content[len(serv["prefix"]):].split(" ")[0]
            if comm_name in moon_server.keys():
                await u_response_moon_server(client, serv, message, comm_name)

        if not message.channel.is_private and message.server.id in not_all_channels_work.keys():
            if message.channel.id in not_all_channels_work[message.server.id] or any(role.permissions.administrator for role in message.author.roles) or (message.author.id == message.server.owner.id):
                await client.process_commands(message)
            else:
                commands_everywhere_list = [
                    "wh",
                    "webhook"
                ]
                if any(message.content.startswith(serv["prefix"]+_name) for _name in commands_everywhere_list):
                    await client.process_commands(message)
        else:
            await client.process_commands(message)
    else:
        tomori = discord.utils.get(message.server.members, id=client.user.id)
        is_external = False
        if not message.channel.is_private and any(role.permissions.administrator or role.permissions.external_emojis for role in tomori.roles) and not message.content.startswith("`"):
            user_badges = await check_badges(conn, message.author.id, "nitro partner")
            content = message.content
            new_content = content


            # if message.server.id in servers_with_removing_urls.keys():
            #     r_count = servers_with_removing_urls[message.server.id]
            #     if r_count == 0 or (r_count >= len(message.author.roles)):
            #         urls = re.findall(re.compile('http[s]?://(?:[a-z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-f][0-9a-f]))+', re.IGNORECASE), new_content)
            #         urls.extend(re.findall(re.compile('discord.gg(?:[a-z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-f][0-9a-f]))+', re.IGNORECASE), new_content))
            #         if urls and not any(role.permissions.administrator for role in message.author.roles):
            #             for url in urls:
            #                 new_content = new_content.replace(url, "[url]")

            if serv["is_nitro"] or any(badge in user_badges for badge in ["nitro", "partner", "staff"]):
                all_emotes = {}
                pattern = r"<:[\w\d_]+:[0-9]+>"
                for match in re.findall(pattern, new_content):
                    i = match.index(":")
                    new_content = new_content.replace(match, match[i:match[i+1:].index(":")+i+2])
                    all_emotes[match[i+1:match[i+1:].index(":")+i+1]] = match
                pattern = r"<a:[\w\d_]+:[0-9]+>"
                for match in re.findall(pattern, new_content):
                    i = match.index(":")
                    new_content = new_content.replace(match, match[i:match[i+1:].index(":")+i+2])
                    all_emotes[match[i+1:match[i+1:].index(":")+i+1]] = match

                pattern = r":[\w\d_]+:"
                replaced = []
                for match in re.findall(pattern, new_content):
                    if match in replaced:
                        continue
                    emoji = discord.utils.get(message.server.emojis, name=match[1:-1])
                    if not emoji:
                        is_external = True
                        emoji = discord.utils.get(client.get_all_emojis(), name=match[1:-1])
                    if emoji and not match in all_emotes.keys():
                        global rq
                        response = rq.get("{base}/guilds/{server}/emojis/{emoji}".format(base=discord_api_url, server=emoji.server.id, emoji=emoji.id))
                        resp = json.loads(response.text)
                        if resp.get("animated", None):
                            pref = "a:"
                        else:
                            pref = ":"
                        name = emoji.name
                        full_emote = "<"+pref+name+":"+emoji.id+">"
                    else:
                        name = match[1:-1]
                        full_emote = all_emotes.get(match[1:-1], match)
                    new_content = re.sub(":"+name+":", full_emote, new_content)
                    replaced.append(match)


                pattern = r"tomori/[a-zA-Z]{3,8}"
                codes = []
                for code in re.findall(pattern, new_content):
                    code_ = code.split("/")[-1]
                    codes.append(code_)

                if new_content != content or codes:
                    urls = re.findall(re.compile('http[s]?://(?:[a-z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-f][0-9a-f]))+', re.IGNORECASE), new_content)
                    urls.extend(re.findall(re.compile('discord.gg(?:[a-z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-f][0-9a-f]))+', re.IGNORECASE), new_content))
                    if urls and not any(role.permissions.administrator for role in message.author.roles):
                        for url in urls:
                            new_content = new_content.replace(url, "[url]")
                    if any(role.permissions.administrator or role.permissions.mention_everyone for role in message.author.roles) != any(role.permissions.administrator or role.permissions.mention_everyone for role in tomori.roles):
                        replace_links = [
                            "@everyone",
                            "@here"
                        ]
                        for link in replace_links:
                            new_content = new_content.replace(link, link[:-1]+"е")
                    if codes:
                        invites = await conn.fetch("SELECT * FROM mods WHERE type = 'custom_invite' AND name IN ('{codes}')".format(
                            codes="','".join(codes)
                        ))
                        for invite in invites:
                            new_content = new_content.replace("tomori/"+invite["name"], invite["value"])
                        if new_content == content:
                            return
                    if is_external:
                        embed = discord.Embed(colour=0x36393f)
                        ava_url = message.author.avatar_url
                        if not ava_url:
                            ava_url = message.author.default_avatar_url
                        embed.set_author(name=message.author.display_name + "#" + message.author.discriminator, icon_url=ava_url)
                        await asyncio.wait([
                            client.delete_message(message),
                            client.send_message(message.channel, content=new_content, embed=embed)
                        ])
                    else:
                        await asyncio.wait([
                            client.delete_message(message),
                            send_webhook(message, content=new_content[:2000], client=client)
                        ])




client.run(settings["token"])
