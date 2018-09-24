import discord
import asyncio
import requests
import logging
import time
from datetime import datetime, date
import string
import random
import copy
import apiai, json
import asyncpg
import copy
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
from cogs.api import *
from cogs.discord_hooks import Webhook


__name__ = "Tomori"
__version__ = "3.20.0"

response_channel_id = "490158714133807134"
global request_channel
request_channel = None


logger = logging.getLogger('tomori')
logger.setLevel(logging.DEBUG)
now = datetime.now()
logname = 'logs/{}_{}.log'.format(now.day, now.month)
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
logname = 'logs/inform->{}_{}.log'.format(now.day, now.month)
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
global client
client = None
global dblpy
dblpy = None
async def get_prefixes():
    global client
    # con = await asyncpg.connect(host="localhost", database="tomori", user=settings["base_user"], password=settings["base_password"])
    # dat = await con.fetch("SELECT prefix FROM settings")
    # prefixes = []
    # if not dat:
    #     prefixes = ["!"]
    # else:
    #     for s in dat:
    #         ss = str(s)[16:17]
    #         if not ss in prefixes:
    #             prefixes.append(ss)
    # await con.close()
    #
    # print(prefixes)
    client = Bot(command_prefix=prefix_list, shard_count=10)
    client.remove_command('help')

async def run_base():
    global conn
    try:
        conn = await asyncpg.create_pool(dsn="postgres://{user}:{password}@{host}:5432/{database}".format(host="localhost", database="tomori", user=settings["base_user"], password=settings["base_password"]), command_timeout=60)
        global top_servers
        top_servers = await conn.fetch("SELECT discord_id FROM settings ORDER BY likes DESC, like_time ASC LIMIT 10")
    except:
        logger.error('PostgreSQL doesn\'t load.\n')
        exit(0)
    await init_locale(conn, client)


loop.run_until_complete(get_prefixes())
loop.run_until_complete(run_base())



def is_it_admin():
    def predicate(ctx):
        if ctx.message.author == ctx.message.server.owner:
            return True
        return any(role.permissions.administrator for role in ctx.message.author.roles)
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
        return ctx.message.author.id in support_list
    return commands.check(predicate)




WORK_COOLDOWN = 1800
WORK_DELAY = 60

async def working():
    await client.wait_until_ready()
    while not client.is_closed:
        now = int(time.time())
        begin_time = datetime.now()
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
        await client.change_presence(game=discord.Game(type=3, name="{servers_count} servers | !help".format(servers_count=len(client.servers))))
        await asyncio.sleep(20)

        users_count = 0
        try:
            for server in client.servers:
                if server.id in not_log_servers:
                    continue
                users_count += len(server.members)
        except:
            pass
        await client.change_presence(game=discord.Game(type=3, name="{users_count} users | !help".format(users_count=users_count)))
        await asyncio.sleep(20)

        # for status in piar_statuses:
        #     await client.change_presence(game=discord.Game(type=1, name=status))
        #     await asyncio.sleep(10)




async def dbl_updating():
    await client.wait_until_ready()
    dblpy = dbl.Client(client, settings["dbl_token"])
    while True:
        try:
            await dblpy.post_server_count()
        except Exception as e:
            pass
        await asyncio.sleep(1800)










@client.event
async def on_server_join(server):
    logger.info("Joined at server - {} | id - {}\n".format(server.name, server.id))
    dat = await conn.fetchrow("SELECT name FROM settings WHERE discord_id = '{}'".format(server.id))
    if not dat:
        lang = "russian"
        if not server.region == "russia":
            lang = "english"
        await conn.execute("INSERT INTO settings(name, discord_id, locale) VALUES('{name}', '{discord_id}', '{locale}')".format(name=clear_name(server.name[:50]), discord_id=server.id, locale=lang))
    await client.send_message(
        client.get_channel(log_join_leave_server_channel_id),
        "Томори добавили на сервер {name} | {id}. ({count} участников)".format(name=server.name, id=server.id, count=len(server.members))
    )
    # for s in admin_list:
    #     await client.send_message(discord.utils.get(client.get_server('327029562535968768').members, id=s), "Томори добавили на сервер {} | {}. ({} участников)".format(server.name, server.id,len(server.members)))

@client.event
async def on_server_remove(server):
    logger.info("Removed from server - {} | id - {}\n".format(server.name, server.id))
    await client.send_message(
        client.get_channel(log_join_leave_server_channel_id),
        "Томори удалили с сервера {name} | {id}. ({count} участников)".format(name=server.name, id=server.id, count=len(server.members))
    )
    # for s in admin_list:
    #     await client.send_message(discord.utils.get(client.get_server('327029562535968768').members, id=s), "Томори удалили с сервера {} | {}.".format(server.name, server.id))

@client.event
async def on_voice_state_update(before, after):
    await u_voice_state_update(client, conn, logger, before, after)

@client.event
async def on_socket_raw_receive(raw_msg):
    if not isinstance(raw_msg, str):
        return
    msg = json.loads(raw_msg)
    type = msg.get("t")
    data = msg.get("d")
    if not data:
        return
    emoji = data.get("emoji")
    user_id = data.get("user_id")
    message_id = data.get("message_id")
    if type == "MESSAGE_REACTION_ADD":
        await u_reaction_add(client, conn, logger, emoji, user_id, message_id)
    if type == "MESSAGE_REACTION_REMOVE":
        await u_reaction_remove(client, conn, logger, emoji, user_id, message_id)








@client.event
async def on_member_join(member):
    logger.info("{0.name} | {0.id} joined at server - {1.name} | {1.id}\n".format(member, member.server))
    if not member.server.id in not_log_servers:
        await client.send_message(client.get_channel('486591862157606913'), "**{2}**\n``({0.name} | {0.mention}) ==> [{1.name} | {1.id}] ({delta} дней)``".format(member, member.server, time.ctime(time.time()), delta=(datetime.utcnow() - member.created_at).days))
    dat = await conn.fetchrow("SELECT autorole_id, welcome_channel_id, locale FROM settings WHERE discord_id = '{id}'".format(id=member.server.id))
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
            c_ban.set_footer(text="ID: {id} • {time}".format(
                id=member.id,
                time=time.ctime(time.time())
            ))
            try:
                await client.send_message(member.server.owner, embed=c_ban)
            except:
                pass

    if dat:
        role = discord.utils.get(member.server.roles, id=dat["autorole_id"])
        if role:
            await client.add_roles(member, role)
        welcome_channel = discord.utils.get(member.server.channels, id=dat["welcome_channel_id"])
        if welcome_channel:
            message = "{who}, добро пожаловать на сервер {server}! Нас уже {count} человек.".format(
                who=member.mention,
                server=member.server.name,
                count=len(member.server.members)
            )
            await client.send_message(welcome_channel, message)


@client.event
async def on_member_remove(member):
    logger.info("{0.name} | {0.id} removed from server - {1.name} | {1.id}\n".format(member, member.server))
    await client.send_message(client.get_channel('486591862157606913'), "*{2}*\n``({0.name} | {0.mention}) <== [{1.name} | {1.id}] ({delta} дней)``".format(member, member.server, time.ctime(time.time()), delta=(datetime.utcnow() - member.created_at).days))
    dat = await conn.fetchrow("SELECT welcome_channel_id FROM settings WHERE discord_id = '{}'".format(member.server.id))
    if dat:
        welcome_channel = discord.utils.get(member.server.channels, id=dat["welcome_channel_id"])
        if welcome_channel:
            message = "{who} покинул нас. Будем ждать снова.".format(who=member.name)
            await client.send_message(welcome_channel, message)








@client.event
async def on_ready():
    dat = await conn.fetch("SELECT name, discord_id FROM settings")
    for server in client.servers:
        if not any(server.id == value["discord_id"] for value in dat):
            try:
                await conn.execute("INSERT INTO settings(name, discord_id) VALUES('{}', '{}')".format(clear_name(server.name[:50]), server.id))
            except:
                pass
    client.loop.create_task(working())
    print('Logged in as')
    logger.info("Logged in as | who - {} | id - {}\n".format(clear_name(client.user.display_name), client.user.id))
    print(clear_name(client.user.display_name))
    print(client.user.id)
    print('------')
    client.loop.create_task(statuses())
    client.loop.create_task(dbl_updating())
    global top_servers
    top_servers = await conn.fetch("SELECT discord_id FROM settings ORDER BY likes DESC, like_time ASC LIMIT 10")
    #await client.change_presence(game=discord.Game(name='Помощь - !help'))
    #await client.change_presence(game=discord.Game(name='бота'))

# @client.event
# async def on_reaction_add(reaction, user):
# 	message_id = reaction.message.id
# 	user_id = user.id
# 	if(reaction.emoji.name == "cookie"):
# 		f_giveaway_add(client, conn, message_id, user)

@client.event
async def on_command_error(error, ctx):
    pass
    if isinstance(error, commands.CommandOnCooldown):
        await client.send_message(ctx.message.channel, "{who}, command is on cooldown. Wait {seconds} seconds".format(who=ctx.message.author.mention, seconds=int(error.retry_after)))
    # elif isinstance(error, commands.MissingRequiredArgument):
    #     await send_cmd_help(ctx)
    # elif isinstance(error, commands.BadArgument):
    #     await send_cmd_help(ctx)

# async def send_cmd_help(ctx):
#     if ctx.invoked_subcommand:
#         pages = client.formatter.format_help_for(ctx, ctx.invoked_subcommand)
#         for page in pages:
#             await client.send_message(ctx.message.channel, page)
#     else:
#         pages = client.formatter.format_help_for(ctx, ctx.command)
#         for page in pages:
#             await client.send_message(ctx.message.channel, page)










@client.command(pass_context=True, name="enable", help="Активировать сервер (Только для меня).")
@commands.cooldown(1, 1, commands.BucketType.user)
@is_it_me()
async def enable(context):
    #logger.info('---------[command]:!enable\n')
    await a_enable(client, conn, context)

@client.command(pass_context=True, name="disable", help="Деактивировать сервер (Только для меня).")
@commands.cooldown(1, 1, commands.BucketType.user)
@is_it_me()
async def disable(context):
    #logger.info('---------[command]:!disable\n')
    await a_disable(client, conn, context)

@client.command(pass_context=True, name="timely", help="Cобрать печенюхи.")
@commands.cooldown(1, 1, commands.BucketType.user)
async def timely(context):
    #logger.info('---------[command]:!timely\n')
    await e_timely(client, conn, context)

@client.command(pass_context=True, name="work", help="Выйти на работу.")
@commands.cooldown(1, 1, commands.BucketType.user)
async def work(context):
    #logger.info('---------[command]:!work\n')
    await e_work(client, conn, context)

@client.command(pass_context=True, name="help", aliases=['commands', 'command', 'helps'], hidden=True, help="Показать список команд.")
@commands.cooldown(1, 1, commands.BucketType.user)
async def helps(context):
    #logger.info('---------[command]:!command\n')
    await o_help(client, conn, context)

@client.command(pass_context=True, name='server', hidden=True, help="Показать информацию о сервере.")
@commands.cooldown(1, 1, commands.BucketType.user)
async def server(context):
    #logger.info('---------[command]:!server\n')
    await o_server(client, conn, context)

@client.command(pass_context=True, name="ping", help="Проверить задержку соединения.")
@commands.cooldown(1, 1, commands.BucketType.user)
async def ping(context):
    #logger.info('---------[command]:!ping\n')
    await o_ping(client, conn, context)

@client.command(pass_context=True, name="hook")
@commands.cooldown(1, 1, commands.BucketType.user)
@is_it_me()
async def hook(context):
    #logger.info('---------[command]:!test\n')
    message = context.message
    try:
        await client.delete_message(message)
    except:
        pass
    msg = Webhook(
        url='https://discordapp.com/api/webhooks/493058039151198230/itqyxwwXtT4U2tNJms7NfNAa6UvrL1rRy3Ol2EjY53YQEoLFC5P8hPAxltgKz0FOYgxS',
        msg=message.content.split(" ", maxsplit=1)[1]
    )
    msg.post()

# @client.command(pass_context=True, name="delete", help="Удалить себя из базы.")
# @commands.cooldown(1, 1, commands.BucketType.user)
# async def delete(context):
#     #logger.info('---------[command]:!delete\n')
#     message = context.message
#     try:
#         await client.delete_message(message)
#     except:
#         pass
#     em = discord.Embed(colour=0xC5934B)
#     try:
#         await conn.execute("DELETE FROM users WHERE discord_id = '{}'".format(message.author.id))
#         em.description = "{} удален из базы.".format(message.author.name)
#     except:
#         em.description = "Не удалось удалить из базы {}.".format(message.author.name)
#     await client.send_message(message.channel, embed=em)

@client.command(pass_context=True, name="createvoice", help="Создать войс канал.")
@commands.cooldown(1, 1, commands.BucketType.user)
async def createvoice(context):
    #logger.info('---------[command]:!createvoice\n')
    await u_createvoice(client, conn, logger, context)

@client.command(pass_context=True, name="region")
@is_it_me()
@commands.cooldown(1, 1, commands.BucketType.user)
async def region(context):
    await client.send_message(context.message.channel, context.message.server.region)

@client.command(pass_context=True, name="setvoice", help="Установить войс канал.")
@commands.cooldown(1, 1, commands.BucketType.user)
async def setvoice(context):
    #logger.info('---------[command]:!setvoice\n')
    await u_setvoice(client, conn, logger, context)

@client.command(pass_context=True, name="setlobby", help="Установить войс для ожидания.")
@commands.cooldown(1, 1, commands.BucketType.user)
async def setlobby(context):
    #logger.info('---------[command]:!setlobby\n')
    await u_setlobby(client, conn, logger, context)

@client.command(pass_context=True, name="say", hidden=True, help="Напишет ваш текст.")
@commands.cooldown(1, 1, commands.BucketType.user)
@is_it_admin()
async def say(context, mes: str=None):
    #logger.info('---------[command]:!say\n')
    await a_say(client, conn, context)

@client.command(pass_context=True, name="say_embed", hidden=True, help="Напишет ваш текст.")
@commands.cooldown(1, 1, commands.BucketType.user)
@is_it_admin()
async def say_embed(context, mes: str=None):
    #logger.info('---------[command]:!say_embed\n')
    await a_say_embed(client, conn, context)

@client.command(pass_context=True, name="find_user", hidden=True)
@commands.cooldown(1, 1, commands.BucketType.user)
@is_it_me()
async def find_user(context, member_id: str=None):
    #logger.info('---------[command]:!find_user\n')
    if not member_id:
        return
    await a_find_user(client, conn, context, member_id)

@client.command(pass_context=True, name="save_roles", hidden=True)
@commands.cooldown(1, 1, commands.BucketType.user)
@is_it_me()
async def save_roles(context):
    #logger.info('---------[command]:!save_roles\n')
    message = context.message
    try:
        await client.delete_message(message)
    except:
        pass
    black_list = message.server.roles
    em = discord.Embed(colour=0xC5934B)
    for s in black_list:
        loggers.info("{0.name} | {0.id}".format(s))
    em.description = "Рол-лист считан!"
    await client.send_message(message.channel, embed=em)

@client.command(pass_context=True, name="save_users", hidden=True, help="Перенести список участников сервера в журнал лога.")
@commands.cooldown(1, 1, commands.BucketType.user)
@is_it_me()
async def save_users(context):
    #logger.info('---------[command]:!save_users\n')
    message = context.message
    try:
        await client.delete_message(message)
    except:
        pass
    users_list = message.server.members
    em = discord.Embed(colour=0xC5934B)
    for s in users_list:
        loggers.info("{0.name} | {0.id}   <->   {1.days} дней  *  {2}".format(s, datetime.utcnow() - s.joined_at, s.joined_at))
    em.description = "Список участников считан!"
    await client.send_message(message.channel, embed=em)

@client.command(pass_context=True, name="base", hidden=True, help="Запрос в базу.")
@commands.cooldown(1, 1, commands.BucketType.user)
@is_it_me()
async def base(context, mes: str=None):
    #logger.info('---------[command]:!base\n')
    await a_base(client, conn, context)

@client.command(pass_context=True, name="news", hidden=True, help="Сделать рассылку заданного сообщения.")
@commands.cooldown(1, 1, commands.BucketType.user)
@is_it_me()
async def news(context, message_id: str=None):
    #logger.info('---------[command]:!news\n')
    await u_news(client, conn, context, message_id)

@client.command(pass_context=True, name="add", hidden=True)
@commands.cooldown(1, 1, commands.BucketType.user)
@is_it_me()
async def add(context, role_id: str=None):
    #logger.info('---------[command]:!add\n')
    message = context.message
    user = message.author
    await client.delete_message(message)
    await client.add_roles(user, discord.utils.get(message.server.roles, id=role_id))

@client.command(pass_context=True, name="del", hidden=True)
@commands.cooldown(1, 1, commands.BucketType.user)
@is_it_me()
async def dele(context, role_id: str=None):
    #logger.info('---------[command]:!del\n')
    message = context.message
    user = message.author
    await client.delete_message(message)
    await client.remove_role(user, discord.utils.get(message.server.roles, id=role_id))

@client.command(pass_context=True, name="invite_server", hidden=True, help="Создать инвайт на данный сервер.")
@commands.cooldown(1, 1, commands.BucketType.user)
@is_it_me()
async def invite_server(context, server_id: str=None):
    #logger.info('---------[command]:!invite_server\n')
    await u_invite_server(client, conn, context, server_id)

@client.command(pass_context=True, name="report", help="Отправить репорт.")
@commands.cooldown(1, 1, commands.BucketType.user)
async def report(context, mes: str=None):
    #logger.info('---------[command]:!report\n')
    await o_report(client, conn, context)

@client.command(pass_context=True, name="give", help="Передать свои печенюхи.")
@commands.cooldown(1, 1, commands.BucketType.user)
async def give(context, who: discord.Member=None, count: str=None):
    #logger.info('---------[command]:!give\n')
    await e_give(client, conn, context, who, count)

@client.command(pass_context=True, name="top", help="Показать топ юзеров.")
@commands.cooldown(1, 1, commands.BucketType.user)
async def top(context, pages: int=None):
    #logger.info('---------[command]:!top\n')
    await e_top(client, conn, context)

@client.command(pass_context=True, name="set", help="Настройка.")
@commands.cooldown(1, 1, commands.BucketType.user)
async def set(context, arg1: str=None, arg2: str=None, *, args: str=None):
    #logger.info('---------[command]:!set\n')
    await o_set(client, conn, context, arg1, arg2, args)

@client.command(pass_context=True, name="backgrounds", aliases=["backs"], help="Показать список фонов.")
@commands.cooldown(1, 1, commands.BucketType.user)
async def backgrounds(context, pages: int=None):
    #logger.info('---------[command]:!backgrounds\n')
    await o_backgrounds(client, conn, context)

@client.command(pass_context=True, name="$", help="Посмотреть свой баланс.")
@commands.cooldown(1, 1, commands.BucketType.user)
async def cash(context):
    #logger.info('---------[command]:!$\n')
    await e_cash(client, conn, context)

@client.command(pass_context=True, name="sex", help="Трахнуть.")
@commands.cooldown(1, 1, commands.BucketType.user)
async def sex(context, who: discord.Member=None):
    #logger.info('---------[command]:!sex\n')
    await f_sex(client, conn, context, who)

@client.command(pass_context=True, name="hug", help="Обнять.")
@commands.cooldown(1, 1, commands.BucketType.user)
async def hug(context, who: discord.Member=None):
    #logger.info('---------[command]:!hug\n')
    await f_hug(client, conn, context, who)

@client.command(pass_context=True, name="wink", help="Подмигнуть.")
@commands.cooldown(1, 1, commands.BucketType.user)
async def wink(context, who: discord.Member=None):
    #logger.info('---------[command]:!wink\n')
    await f_wink(client, conn, context, who)

@client.command(pass_context=True, name="five", help="Дать пять.")
@commands.cooldown(1, 1, commands.BucketType.user)
async def five(context, who: discord.Member=None):
    #logger.info('---------[command]:!five\n')
    await f_five(client, conn, context, who)

@client.command(pass_context=True, name="fuck", help="Показать фак.")
@commands.cooldown(1, 1, commands.BucketType.user)
async def fuck(context, who: discord.Member=None):
    #logger.info('---------[command]:!fuck\n')
    await f_fuck(client, conn, context, who)

@client.command(pass_context=True, name="punch", help="Дать леща.")
@commands.cooldown(1, 1, commands.BucketType.user)
async def punch(context, who: discord.Member=None):
    #logger.info('---------[command]:!punch\n')
    await f_punch(client, conn, context, who)

@client.command(pass_context=True, name="kiss", help="Поцеловать.")
@commands.cooldown(1, 1, commands.BucketType.user)
async def kiss(context, who: discord.Member=None):
    #logger.info('---------[command]:!kiss\n')
    await f_kiss(client, conn, context, who)

@client.command(pass_context=True, name="drink", help="Уйти в запой.")
@commands.cooldown(1, 1, commands.BucketType.user)
async def drink(context):
    #logger.info('---------[command]:!drink\n')
    await f_drink(client, conn, context)

@client.command(pass_context=True, name="shiki", help="Найти аниме на Shikimori.")
@commands.cooldown(1, 1, commands.BucketType.user)
async def shiki(context, *, name: str=None):
    #logger.info('---------[command]:!br\n')
    await api_shiki(client, conn, logger, context, name)

@client.command(pass_context=True, name="google", help="Найти что-то в гугле.")
@commands.cooldown(1, 1, commands.BucketType.user)
async def google_search(context, *, name: str=None):
    #logger.info('---------[command]:!br\n')
    await api_google_search(client, conn, logger, context, name)

@client.command(pass_context=True, name="br", aliases=["roll"], help="Поставить деньги на рулетке.")
@commands.cooldown(1, 2, commands.BucketType.user)
async def br(context, count: str=None):
    #logger.info('---------[command]:!br\n')
    await e_br(client, conn, context, count)

@client.command(pass_context=True, name="slots", aliases=["slot"], help="Поставить деньги на рулетке.")
@commands.cooldown(1, 2, commands.BucketType.user)
async def slots(context, count: str=None):
    #logger.info('---------[command]:!slots\n')
    await e_slots(client, conn, context, count)

@client.command(pass_context=True, name="rep", help="Выразить свое почтение.")
@commands.cooldown(1, 1, commands.BucketType.user)
async def rep(context, who: discord.Member=None):
    #logger.info('---------[command]:!rep\n')
    await f_rep(client, conn, context, who)

@client.command(pass_context=True, name="setall")
@is_it_me()
async def setall(context, role_id: str=None):
    #logger.info('---------[command]:!setall\n')
    message = context.message
    role = discord.utils.get(message.server.roles, id=role_id)
    if not role:
        return
    for member in message.server.members:
        if not role in member.roles:
            await client.add_roles(member, role)


@client.command(pass_context=True, name="avatar", help="Показать аватар пользователя.")
@commands.cooldown(1, 1, commands.BucketType.user)
async def avatar(context, who: discord.Member=None):
    await o_avatar(client, conn, context, who)

@client.command(pass_context=True, name="me", help="Вывести статистику пользователя картинкой.")
@commands.cooldown(1, 15, commands.BucketType.user)
async def me(context):
    await f_me(client, conn, context)

@client.command(pass_context=True, name="unfriend")
@commands.cooldown(1, 1, commands.BucketType.user)
@is_it_me()
async def unfriend(context, who_id: str=None, * , reason: str=None):
    await a_unfriend(client, conn, context, who_id, reason)

@client.command(pass_context=True, name="kick", help="Кикнуть пользователя.")
@commands.cooldown(1, 1, commands.BucketType.user)
async def kick(context, who: discord.Member=None, reason: str=None):
    await a_kick(client, conn, context, who, reason)

@client.command(pass_context=True, name="ban", help="Забанить пользователя.")
@commands.cooldown(1, 1, commands.BucketType.user)
async def ban(context, who: discord.Member=None, reason: str=None):
    await a_ban(client, conn, context, who, reason)

@client.command(pass_context=True, name="unban", help="Разбанить пользователя.")
@commands.cooldown(1, 1, commands.BucketType.user)
async def unban(context, whos: str=None, reason: str=None):
    await a_unban(client, conn, context, whos, reason)

@client.command(pass_context=True, name="start", help="Test.")
@commands.cooldown(1, 1, commands.BucketType.user)
@is_it_admin_or_dev()
async def start(context, channel_id: str=None, *, name: str=None):
    if not channel_id:
        return
    #logger.info('---------[command]:!start\n')
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
    #logger.info('---------[command]:!stop\n')
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

@client.command(pass_context=True, name="clear", hidden=True, help="Удалить последние сообщения.")
@commands.cooldown(1, 1, commands.BucketType.user)
async def clear(context, count: int=None, who: discord.Member=None):
    #logger.info('---------[command]:!clear\n')
    await a_clear(client, conn, context, count, who)

@client.command(pass_context=True, name="about", help="Показать информацию о боте.")
@commands.cooldown(1, 1, commands.BucketType.user)
async def about(context):
    #logger.info('---------[command]:!about\n')
    await o_about(client, conn, context)

@client.command(pass_context=True, name="like")
@commands.cooldown(1, 10, commands.BucketType.user)
async def like(context):
    #logger.info('---------[command]:!like\n')
    await o_like(client, conn, context)

@client.command(pass_context=True, name="list")
@commands.cooldown(1, 1, commands.BucketType.user)
async def list(context, page: int=None):
    #logger.info('---------[command]:!list\n')
    await o_list(client, conn, context, page)

@client.command(pass_context=True, name="invite", help="Получить ссылку на добавление бота себе на сервер.")
@commands.cooldown(1, 1, commands.BucketType.user)
async def invite(context):
    #logger.info('---------[command]:!invite\n')
    await o_invite(client, conn, context)

@client.command(pass_context=True, name="giveaway", help="Начать розыгрыш.")
@commands.cooldown(1, 1, commands.BucketType.user)
async def giveaway(context, count: int=300, message: str="Розыгрыш!"):
	#logger.info('---------[command]:!giveaway\n')
	global conn
	await f_giveaway(client, conn, context, count, message)


@client.event
async def on_message(message):
    await u_check_support(client, conn, logger, message)

    if "᠌" in message.content:
        await client.delete_message(message)

    if not message.channel.is_private:
        logger.info("server - {} | server_id - {} | channel - {} | name - {} | mention - {} | message_id - {}\ncontent - {}\n".format(message.server.name, message.server.id, message.channel.name, message.author.name,message.author.mention, message.id, message.content))
    else:
        logger.info("private_message | name - {} | mention - {} | message_id - {}\ncontent - {}\n".format(message.author.name,message.author.mention, message.id, message.content))
        await client.process_commands(message)
        return

    server_id = message.server.id
    serv = await conn.fetchrow("SELECT prefix, xp_cooldown, is_enable FROM settings WHERE discord_id = \'{}\'".format(server_id))
    if message.author.bot or not serv or not serv[2]:
        return

    dat = await conn.fetchrow("SELECT xp_time, xp_count, messages, cash FROM users WHERE discord_id = '{}'".format(message.author.id))
    t = int(time.time())
    if dat:
        if (int(t) - dat["xp_time"]) >= serv["xp_cooldown"]:
            global top_servers
            count = 2
            if any(server_id == server["discord_id"] for server in top_servers):
                count *= 2
            await conn.execute("UPDATE users SET xp_time = {time}, xp_count = {count}, messages = {messages}, cash = {cash} WHERE discord_id = '{id}'".format(
                time=t,
                count=dat["xp_count"] + 1,
                messages=dat["messages"]+1,
                cash=dat["cash"] + count,
                id=message.author.id)
            )
        await conn.execute("UPDATE users SET messages = {messages} WHERE discord_id = '{id}'".format(
            messages=dat["messages"]+1,
            id=message.author.id)
        )
    else:
        await conn.execute("INSERT INTO users(name, discord_id, discriminator, xp_count, xp_time, messages, background) VALUES('{}', '{}', '{}', {}, {}, {}, '{}')".format(clear_name(message.author.display_name[:50]), message.author.id, message.author.discriminator, 1, t, 1, random.choice(background_list)))

    if message.content.startswith(serv[0]) or message.content.startswith("!help"):
        await client.process_commands(message)



def max(list):
    maximum = -1
    p = 0
    for s in range(len(list)):
        if int(list[s]) > maximum:
            maximum = int(list[s])
            p = s
    return p

async def strcmp(s1, s2):
    i1 = 0
    i2 = 0
    s1 = s1 + '\0'
    s2 = s2 + '\0'
    while ((s1[i1] != '\0') & (s2[i2] != '\0')):
        if(s1[i1] != s2[i2]):
            return 0
        i1 = i1 + 1
        i2 = i2 + 1
    if(s1[i1] != s2[i2]):
        return 0
    else:
        return 1

client.run(settings["token"])
