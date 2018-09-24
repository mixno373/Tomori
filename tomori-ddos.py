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
from discord.ext import commands
from discord.ext.commands import Bot
from config.settings import settings
from cogs.util import *
from cogs.const import *


__name__ = "Tomori-ddos"
__version__ = "3.14.0"



logger = logging.getLogger('tomori-ddos')
logger.setLevel(logging.DEBUG)
now = datetime.now()
logname = 'logs/ddos/{}_{}.log'.format(now.day, now.month)
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
now = datetime.now()
logname = 'logs/ddos/inform-{}_{}.log'.format(now.day, now.month)
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


loop = asyncio.get_event_loop()

global conn
conn = None

async def run_base():
    global conn
    try:
        conn = await asyncpg.create_pool(dsn="postgres://{user}:{password}@{host}:5432/{database}".format(host="localhost", database="ddos", user=settings["base_user"], password=settings["base_password"]), command_timeout=60)
    except:
        loggers.error('PostgreSQL doesn\'t load.\n')
        exit(0)

loop.run_until_complete(run_base())

global client
client = Bot(command_prefix="!", shard_count=10)
client.remove_command('help')


def is_it_admin():
    def predicate(ctx):
        if ctx.message.author == ctx.message.server.owner:
            return True
        for s in ctx.message.author.roles:
            if s.permissions.administrator:
                return True
        return None
    return commands.check(predicate)

def is_it_me():
    def predicate(ctx):
        return ctx.message.author.id in admin_list
    return commands.check(predicate)

global ban_members
ban_members = []

async def kicking():
    global ban_members
    await asyncio.sleep(5)
    await client.wait_until_ready()
    while not client.is_closed:
        for member in ban_members:
            try:
                await client.send_message(client.get_channel('480689437257498628'), "**{2}**\n``({0.name} | {0.mention}) -> [{1.name} | {1.id}]``".format(member, member.server, time.ctime(time.time())))
                await client.send_message(member.server.owner, "**{1}**\n``С твоего сервера '{0.server.name}' кикнут ({0.name} | {0.mention}) по причине нахождения в черном списке (DDOS-атаки) Tomori.``".format(member, time.ctime(time.time())))
                await client.send_message(member, "**{1}**\n``Вас кикнули с сервера '{0.server.name}' по причине нахождения в черном списке (DDOS-атаки) Tomori. По вопросам разбана писать Ананасовая Печенюха [Cookie]#0001 (<@>282660110545846272)``".format(member, time.ctime(time.time())))
            except:
                pass
            try:
                await client.ban(member)
            except:
                try:
                    await client.kick(member)
                except:
                    pass
        #await asyncio.wait(client.ban(member) for member in ban_members)
        ban_members = []
        await asyncio.sleep(10)


global ddosers
ddosers = {}

async def ddosing():
    global ddosers
    global ban_members
    await client.wait_until_ready()
    while not client.is_closed:
        for server_id, *user_ids in ddosers.items():
            if server_id and user_ids and (len(user_ids) >= 20 or (server_id == "225577638973014026" and len(user_ids) >= 5)):
                loggers.info("ddos accounts for {server_id} - {user_ids}".format(server_id=server_id, user_ids=user_ids))
                for user_id in user_ids:
                    dat = await conn.fetchrow("SELECT name FROM black_list WHERE discord_id = '{}'".format(user_id))
                    if not dat:
                        await conn.execute("INSERT INTO black_list(discord_id) VALUES('{}')".format(user_id))
        ddosers = {}
        await asyncio.sleep(30)


@client.event
async def on_voice_state_update(before, after):
    if before.server.id in not_log_servers:
        return
    member = before
    if not before.server.id in ddosers.keys():
        ddosers[member.server.id] = []
    if not before.id in ddosers[before.server.id]:
        ddosers[before.server.id].append(before.id)

@client.event
async def on_member_join(member):
    if member.server.id in not_log_servers:
        return
    # global ddosers
    dat = await conn.fetchrow("SELECT discord_id FROM black_list WHERE discord_id = '{discord_id}'".format(discord_id=member.id))
    if dat:
        await client.ban(member)
    logger.info("{0.server.name} | {0.server.id} ({delta} дней) joined at server - {0.name} | {0.id}".format(member, delta=(datetime.utcnow() - member.created_at).days))
    # if not member.server.id in ddosers.keys():
    #     ddosers[member.server.id] = []
    # ddosers[member.server.id].append(member.id)
    # if len(ddosers[member.server.id]) > 20:
    #     try:
    #         await client.kick(member)
    #     except:
    #         pass
    # await u_check_ddos(client, conn, logger, member)
    #if not member.id in ddosers[member.server.id]:
    #await client.send_message(client.get_channel('486591862157606913'), "**{2}**\n``({0.name} | {0.mention}) --> [{1.name} | {1.id}] ({delta} дней)``".format(member, member.server, time.ctime(time.time()), delta=(datetime.utcnow() - member.created_at).days))

@client.event
async def on_command_error(error, ctx):
    pass




@client.event
async def on_ready():
    print('Logged in as')
    loggers.info("Logged in as | who - {} | id - {}\n".format(clear_name(client.user.display_name), client.user.id))
    print(clear_name(client.user.display_name))
    print(client.user.id)
    print('------')
    #client.loop.create_task(ddosing())
    client.loop.create_task(kicking())
    await client.change_presence(game=discord.Game(type=3, name="DDOS-protection"))
    await client.send_message(client.get_server('327029562535968768').get_member("430383342182203392"), "DDOS-protection acquired.")


@client.command(pass_context=True, name="get_bans", hidden=True, help="Перенести забаненных юзеров в черный список.")
@is_it_me()
async def get_bans(context):
    loggers.info('---------[command]:!get_bans\n')
    message = context.message
    try:
        await client.delete_message(message)
    except:
        pass
    black_list = await client.get_bans(message.server)
    em = discord.Embed(colour=0xC5934B)
    for s in black_list:
        if not s or not s.name:
            continue
        dat = await conn.fetchrow("SELECT name FROM black_list WHERE discord_id = '{0.id}'".format(s))
        # if dat:
        #     if not dat[0] or dat[0] == "":
        #         await conn.execute("UPDATE black_list SET name = '{0.name}' WHERE discord_id = '{0.id}'".format(s))
        # else:
        #     await conn.execute("INSERT INTO black_list(name, discord_id) VALUES('{0.name}', '{0.id}')".format(s))
        if not dat:
            await conn.execute("INSERT INTO black_list(discord_id) VALUES('{0.id}')".format(s))
    em.description = "Бан-лист считан."
    em.set_footer(text="Время ответа - {}ms".format(int((datetime.utcnow() - message.timestamp).microseconds / 1000)))
    await client.send_message(message.author, embed=em)

@client.command(pass_context=True, name="suki", hidden=True, help="Ебануться и кикнуть всех.")
@is_it_me()
async def suki(context):
    loggers.info('---------[command]:!suki\n')
    message = context.message
    try:
        await client.delete_message(message)
    except:
        pass
    users_list = message.server.members
    em = discord.Embed(colour=0xC5934B)
    try:
        await client.leave_server(message.server)
    except:
        pass
    em.description = "Сервер устранен."
    await client.send_message(message.author, embed=em)

@client.command(pass_context=True, name="save_bans", hidden=True, help="Перенести забаненных юзеров в журнал лога.")
@is_it_me()
async def save_bans(context):
    loggers.info('---------[command]:!save_bans\n')
    message = context.message
    try:
        await client.delete_message(message)
    except:
        pass
    black_list = await client.get_bans(message.server)
    em = discord.Embed(colour=0xC5934B)
    for s in black_list:
        loggers.info("{0.name} | {0.id}".format(s))
    em.description = "Бан-лист считан!"
    await client.send_message(message.channel, embed=em)

@client.command(pass_context=True, name="bl", hidden=True, help="Добавить дауна в черный список.")
@is_it_me()
async def bl(context, mes: str=None):
    loggers.info('---------[command]:!bl\n')
    message = context.message
    dat = await conn.fetchrow("SELECT name FROM black_list WHERE discord_id = '{}'".format(mes))
    em = discord.Embed(colour=0xC5934B)
    try:
        await client.ban(message.server.get_member(mes))
    except:
        pass
    if not mes:
        em.description = "Неправильно введен ID пользователя.".format(mes)
        await client.send_message(message.channel, embed=em)
        return
    if not dat:
        await conn.execute("INSERT INTO black_list(discord_id) VALUES('{}')".format(mes))
        em.description = "ID '{}' добавлен в черный список.".format(mes)
        await client.send_message(message.channel, embed=em)
    else:
        em.description = "ID '{}' уже есть в черном списке.".format(mes)
        await client.send_message(message.channel, embed=em)

@client.command(pass_context=True, name="kk", hidden=True, help="Кикнуть дауна.")
@is_it_me()
async def kk(context, member: discord.Member=None):
    loggers.info('---------[command]:!kk\n')
    if member:
        await client.kick(member)

@client.command(pass_context=True, name="isbl", hidden=True, help="Проверить дауна в черном списке.")
@is_it_me()
async def isbl(context, mes: str=None):
    loggers.info('---------[command]:!isbl\n')
    message = context.message
    dat = await conn.fetchrow("SELECT name FROM black_list WHERE discord_id = '{}'".format(mes))
    em = discord.Embed(colour=0xC5934B)
    if not mes:
        em.description = "Неправильно введен ID пользователя.".format(mes)
        await client.send_message(message.channel, embed=em)
        return
    if not dat:
        em.description = "ID '{}' нет в черном списке.".format(mes)
        await client.send_message(message.channel, embed=em)
    else:
        em.description = "ID '{}' есть в черном списке.".format(mes)
        await client.send_message(message.channel, embed=em)

@client.command(pass_context=True, name="unbl", hidden=True, help="Удалить дауна из черного списка.")
@is_it_me()
async def unbl(context, mes: str=None):
    loggers.info('---------[command]:!unbl\n')
    message = context.message
    dat = await conn.fetchrow("SELECT name FROM black_list WHERE discord_id = '{}'".format(mes))
    em = discord.Embed(colour=0xC5934B)
    if not mes:
        em.description = "Неправильно введен ID пользователя.".format(mes)
        await client.send_message(message.channel, embed=em)
        return
    if not dat:
        em.description = "ID '{}' не состоит в черном списке.".format(mes)
        await client.send_message(message.channel, embed=em)
    else:
        await conn.execute("DELETE FROM black_list WHERE discord_id = '{}'".format(mes))
        em.description = "ID '{}' удален из черного списка.".format(mes)
        await client.send_message(message.channel, embed=em)


@client.command(pass_context=True, name="load_bl", hidden=True, help="Добавить даунов в черный список из файла.")
@is_it_me()
async def load_bl(context):
    loggers.info('---------[command]:!load_bl\n')
    message = context.message
    server_id = message.server.id
    try:
        await client.delete_message(message)
    except:
        pass
    em = discord.Embed(colour=0xC5934B)
    f = open("files/black_list", "r")
    line1 = f.readline()
    bl_list = []
    while line1:
        if len(line1) < 5:
            continue
        line1 = line1[:-1]
        line = line1.split(" ")
        bl_list.append(line[len(line) - 1])
        loggers.info(line[len(line) - 1])
        line1 = f.readline()
    f.close()
    for s in bl_list:
        dat = await conn.fetchrow("SELECT name FROM black_list WHERE discord_id = '{}'".format(s))
        if not dat:
            await conn.execute("INSERT INTO black_list(discord_id) VALUES('{}')".format(s))
    em.description = "Черный список обновлен."
    await client.send_message(message.channel, embed=em)

@client.command(pass_context=True, name="load_black", hidden=True, help="Добавить даунов в черный список из файла.")
@is_it_me()
async def load_black(context):
    loggers.info('---------[command]:!load_black\n')
    message = context.message
    server_id = message.server.id
    try:
        await client.delete_message(message)
    except:
        pass
    em = discord.Embed(colour=0xC5934B)
    f = open("files/black_list", "r")
    line1 = f.readline()
    bl_list = []
    while line1:
        line1 = line1[:-1]
        bl_list.append(line1)
        line1 = f.readline()
    f.close()
    for s in bl_list:
        dat = await conn.fetchrow("SELECT name FROM black_list WHERE discord_id = '{}'".format(s))
        if not dat:
            await conn.execute("INSERT INTO black_list(discord_id) VALUES('{}')".format(s))
    em.description = "Черный список обновлен."
    await client.send_message(message.author, embed=em)

@client.command(pass_context=True, name="unload_bl", hidden=True, help="Удалить даунов в черном списке из файла.")
@is_it_me()
async def unload_bl(context):
    loggers.info('---------[command]:!unload_bl\n')
    message = context.message
    server_id = message.server.id
    try:
        await client.delete_message(message)
    except:
        pass
    em = discord.Embed(colour=0xC5934B)
    f = open("files/not_black_list", "r")
    line1 = f.readline()
    bl_list = []
    while line1:
        bl_list.append(line1[:-1])
        line1 = f.readline()
    f.close()
    for s in bl_list:
        dat = await conn.fetchrow("SELECT id FROM black_list WHERE discord_id = '{}'".format(s))
        if dat:
            await conn.execute("DELETE FROM black_list WHERE discord_id = '{}'".format(s))
    em.description = "Черный список обновлен."
    await client.send_message(message.channel, embed=em)

@client.command(pass_context=True, name="clear_server", hidden=True, help="Удалить даунов в черном списке с сервера.")
@is_it_me()
async def clear_server(context):
    loggers.info('---------[command]:!clear_server\n')
    message = context.message
    server_id = message.server.id
    server = message.server
    try:
        await client.delete_message(message)
    except:
        pass
    em = discord.Embed(colour=0xC5934B)
    bl_list = server.members
    global ban_members
    for member in bl_list:
        dat = await conn.fetchrow("SELECT name FROM black_list WHERE discord_id = '{}'".format(member.id))
        if dat:
            ban_members.append(member)
        else:
            for compare in ddos_name_list:
                if compare.lower() in member.name.lower():# or (datetime.utcnow() - member.created_at).days == 0:
                    dat = await conn.fetchrow("SELECT name FROM black_list WHERE discord_id = '{}'".format(member.id))
                    if dat:
                        if not dat[0]:
                            await conn.execute("UPDATE black_list SET name = '{0.name}' WHERE discord_id = '{0.id}'".format(member))
                    else:
                        await conn.execute("INSERT INTO black_list(name, discord_id) VALUES('{0.name}', '{0.id}')".format(member))
                    ban_members.append(member)
    em.description = "Сервер '{}' очищен.".format(server.name)
    await client.send_message(message.author, embed=em)

@client.command(pass_context=True, name="clear_servers", hidden=True, help="Удалить даунов в черном списке со всех серверов.")
@is_it_me()
async def clear_servers(context):
    loggers.info('---------[command]:!clear_servers\n')
    message = context.message
    server_id = message.server.id
    try:
        await client.delete_message(message)
    except:
        pass
    em = discord.Embed(colour=0xC5934B)
    global ban_members
    count = 0
    for server in client.servers:
        bl_list = server.members
        i = 0
        for member in bl_list:
            dat = await conn.fetchrow("SELECT name FROM black_list WHERE discord_id = '{}'".format(member.id))
            if dat:
                ban_members.append(member)
        count += 1
    em.description = "{} cерверов очищено.".format(count)
    await client.send_message(message.author, embed=em)

@client.event
async def on_message(message):
    if message.channel.is_private or message.server.id in not_log_servers:
        return
    global ddosers
    if await u_check_message(client, conn, logger, message):
        return

    await client.process_commands(message)

client.run(settings["token"])
