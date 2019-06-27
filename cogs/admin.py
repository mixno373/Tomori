import discord
import asyncio
import requests
import time
from datetime import datetime, date, timedelta
import string
import random
import copy
import os
import re
import json
import asyncpg
from discord.ext import commands
from cogs.const import *
from cogs.ids import *
from cogs.locale import *
from cogs.util import *
from config.constants import *

async def a_enable(client, conn, context):
    message = context.message
    server_id = message.server.id
    try:
        await client.delete_message(message)
    except:
        pass
    await conn.execute("UPDATE settings SET "+
        "is_timely = True, " +
        "is_lb = True, " +
        "is_cash = True, " +
        "is_gift = True, " +
        "is_enable = True, " +
        "is_say = True, " +
        "is_profile = True, " +
        "is_hug = True, " +
        "is_five = True, " +
        "is_punch = True, " +
        "is_fuck = True, " +
        "is_kiss = True, " +
        "is_drink = True, " +
        "is_wink = True, " +
        "is_give = True, " +
        "is_rep = True, " +
        "is_clear = True, " +
        "is_avatar = True, " +
        "is_take = True, " +
        "is_work = True, " +
        "is_br = True, " +
        "is_slots = True, " +
        "is_me = True, " +
        "is_ban = True, " +
        "is_kick = True, " +
        "is_news = True, " +
        "is_marry = True, " +
        "is_createvoice = True " +
        "WHERE discord_id = '{}'".format(server_id))
    pop_cached_server(server_id)
    await client.send_message(message.author, "Сервер '{} | {}' активирован.".format(message.server.name, message.server.id))
    return

async def a_disable(client, conn, context):
    message = context.message
    server_id = message.server.id
    try:
        await client.delete_message(message)
    except:
        pass
    await conn.execute("UPDATE settings SET "+
        "is_timely = False, " +
        "is_lb = False, " +
        "is_cash = False, " +
        "is_gift = False, " +
        "is_enable = False, " +
        "is_say = False, " +
        "is_profile = False, " +
        "is_hug = False, " +
        "is_five = False, " +
        "is_punch = False, " +
        "is_fuck = False, " +
        "is_kiss = False, " +
        "is_drink = False, " +
        "is_wink = False, " +
        "is_give = False, " +
        "is_rep = False, " +
        "is_clear = False, " +
        "is_avatar = False, " +
        "is_take = False, " +
        "is_work = False, " +
        "is_br = False, " +
        "is_slots = False, " +
        "is_me = False, " +
        "is_ban = False, " +
        "is_kick = False, " +
        "is_news = False, " +
        "is_marry = False, " +
        "is_createvoice = False " +
        "WHERE discord_id = '{}'".format(server_id))
    pop_cached_server(server_id)
    await client.send_message(message.author, "Сервер '{} | {}' деактивирован.".format(message.server.name, message.server.id))
    return

async def a_say(client, conn, context, value):
    message = context.message
    server_id = message.server.id
    temp = value.split(" ", maxsplit=1)
    channel = message.channel
    if len(temp) > 1:
        channel = temp[0]
        channel = re.sub(r'[<@#&!>]+', '', channel)
        channel = client.get_channel(channel)
        if channel:
            value = temp[1]
        else:
            channel = message.channel
    const = await get_cached_server(conn, server_id)
    lang = const["locale"]
    if not lang in locale.keys():
        em = discord.Embed(description="{who}, {response}.".format(
            who=tagged_dname(message.author),
            response="ошибка локализации",
            colour=0xC5934B))
        await client.send_message(message.channel, embed=em)
        return
    em = discord.Embed(colour=int(const["em_color"], 16) + 512)
    if not const or not const["is_say"]:
        em.description = locale[lang]["global_not_available"].format(who=tagged_dname(message.author))
        await client.send_message(message.channel, embed=em)
        return
    text, em = await get_embed(value)
    await asyncio.wait([
        client.delete_message(message),
        client.send_message(channel, content=text, embed=em)
    ])
    return

async def a_send(client, conn, context, url):
    message = context.message
    server_id = message.server.id
    const = await get_cached_server(conn, server_id)
    lang = const["locale"]
    if not lang in locale.keys():
        em = discord.Embed(description="{who}, {response}.".format(
            who=tagged_dname(message.author),
            response="ошибка локализации"),
            colour=0xC5934B)
        await client.send_message(message.channel, embed=em)
        return
    em = discord.Embed(colour=int(const["em_color"], 16) + 512)
    if not const:
        em.description = locale[lang]["global_not_available"].format(who=tagged_dname(message.author))
        await client.send_message(message.channel, embed=em)
        return
    try:
        await client.delete_message(message)
    except:
        pass
    await client.send_typing(message.channel)
    try:
        name = "files/send/"+message.author.id+"_"+url.rsplit("/", maxsplit=1)[1]
        f = open(name,"wb")
        req = requests.get(url)
        f.write(req.content)
        f.close()
    except:
        em.description = locale[lang]["global_check_url"].format(
            who=tagged_dname(message.author),
            url=url
        )
        await client.send_message(message.channel, embed=em)
        return
    await client.upload(name)
    os.remove(name)
    return

async def a_find_owner(client, conn, context, member_id):
    message = context.message
    em = discord.Embed(colour=0xC5934B)
    servers_count = 0
    name = ""
    memb = message.author
    for server in client.servers:
        member = server.get_member(member_id)
        if member and server.owner and member.id == server.owner.id:
            memb = member
            name = tagged_dname(member) + " | "
            servers_count += 1
            em.add_field(
                name="#"+str(servers_count)+" "+server.name,
                value=server.id,
                inline=True
            )
            break
    name = name + member_id
    em.title = "Servers by {name}".format(name=name)
    icon_url = message.author.avatar_url
    if not icon_url:
        icon_url = message.author.default_avatar_url
    em.set_footer(text=tagged_dname(message.author), icon_url=icon_url)
    await asyncio.wait([
        client.delete_message(message),
        client.send_message(message.channel, embed=em)
    ])
    if member_id in admin_list and memb.id != message.author.id:
        em = discord.Embed(
            title="Tomori find owner",
            description="Твои сервера искал `{who}`".format(who=tagged_dname(message.author)),
            colour=0xC5934B
        )
        await client.send_message(memb, embed=em)

async def a_find_user(client, conn, context, member_id):
    message = context.message
    em = discord.Embed(colour=0xC5934B)
    servers_count = 0
    name = ""
    memb = message.author
    for server in client.servers:
        member = server.get_member(member_id)
        if member:
            memb = member
            name = tagged_dname(member) + " | "
            servers_count += 1
            em.add_field(
                name="#"+str(servers_count)+" "+server.name,
                value=server.id,
                inline=True
            )
        member = None
    name = name + member_id
    em.title = "Servers with {name}".format(name=name)
    icon_url = message.author.avatar_url
    if not icon_url:
        icon_url = message.author.default_avatar_url
    em.set_footer(text=tagged_dname(message.author), icon_url=icon_url)
    await asyncio.wait([
        client.delete_message(message),
        client.send_message(message.channel, embed=em)
    ])
    if member_id in admin_list and memb.id != context.message.author.id:
        em = discord.Embed(
            title="Tomori find user",
            description="Сервера с тобой искал `{who}`".format(who=tagged_dname(message.author)),
            colour=0xC5934B
        )
        await client.send_message(memb, embed=em)

async def a_find_voice(client, conn, context, member_id):
    message = context.message
    em = discord.Embed(colour=0xC5934B)
    servers_count = 0
    name = ""
    memb = message.author
    for server in client.servers:
        member = server.get_member(member_id)
        if member and member.voice.voice_channel:
            memb = member
            name = tagged_dname(member) + " | "
            servers_count += 1
            em.add_field(
                name="#"+str(servers_count)+" "+server.name+" • "+server.id,
                value=member.voice.voice_channel.name+" • "+member.voice.voice_channel.id,
                inline=True
            )
        member = None
    name = name + member_id
    em.title = "Voices with {name}".format(name=name)
    icon_url = message.author.avatar_url
    if not icon_url:
        icon_url = message.author.default_avatar_url
    em.set_footer(text=tagged_dname(message.author), icon_url=icon_url)
    await asyncio.wait([
        client.delete_message(message),
        client.send_message(message.channel, embed=em)
    ])
    if member_id in admin_list and memb.id != context.message.author.id:
        em = discord.Embed(
            title="Tomori find voice",
            description="Войсы с тобой искал `{who}`".format(who=tagged_dname(message.author)),
            colour=0xC5934B
        )
        await client.send_message(memb, embed=em)

async def a_base(client, conn, context, request):
    message = context.message
    lang = "english"
    em = discord.Embed(colour=0xC5934B)
    try:
        response = await conn.fetchrow(request)
        em.description = locale[lang]["admin_request_completed"].format(request) #Запрос '''{}''' успешно выполнен.
        count = 0
        if response:
            for name, value in response.items():
                count += 1
                value_ = "'{}'".format(value) if isinstance(value, str) else str(value)
                em.add_field(
                    inline=True,
                    name=str(name),
                    value=value_
                )
                if count % 25 == 0 and count != len(response):
                    await client.send_message(message.channel, embed=em)
                    em = discord.Embed(colour=0xC5934B)
    except:
        em.description = locale[lang]["admin_request_failed"].format(request) #Не удалось выполнить запрос '''{}'''
    await asyncio.wait([
        client.delete_message(message),
        client.send_message(message.channel, embed=em),
        clear_caches()
    ])
    return

global who_user
who_user = None
def is_user(m):
    return m.author == who_user

async def a_clear(client, conn, context, count, who):
    message = context.message
    server_id = message.server.id
    server = message.server
    author = message.author
    const = await get_cached_server(conn, server_id)
    lang = const["locale"]
    if not lang in locale.keys():
        em = discord.Embed(description="{who}, {response}.".format(
            who=tagged_dname(message.author),
            response="ошибка локализации"),
            colour=0xC5934B)
        await client.send_message(message.channel, embed=em)
        return
    em = discord.Embed(colour=int(const["em_color"], 16) + int("0x200", 16))
    if not const or not const["is_clear"]:
        em.description = locale[lang]["global_not_available"].format(who=tagged_dname(message.author))
        await client.send_message(message.channel, embed=em)
        return
    if not author == server.owner:# and not author.id in admin_list:
        for role in author.roles:
            if role.permissions.manage_messages or role.permissions.administrator:
                break
        else:
            em.description = locale[lang]["global_not_allow_to_use"].format(tagged_dname(message.author)) #{}, у тебя нет прав
            await client.send_message(message.channel, embed=em)
            return
    if not count:
        em.description = locale[lang]["global_not_number"].format(clear_name(tagged_dname(message.author))) #{}, введенное значение не является числом.
        await client.send_message(message.channel, embed=em)
        return
    if who:
        global who_user
        who_user = who
        if not message.author == who:
            await client.delete_message(message)
        await client.purge_from(message.channel, limit=count + 1, check=is_user)
    else:
        await client.purge_from(message.channel, limit=count + 1)
    return

async def a_take(client, conn, context, who, count):
    message = context.message
    server_id = message.server.id
    server = message.server
    author = message.author
    const = await get_cached_server(conn, server_id)
    lang = const["locale"]
    if not lang in locale.keys():
        em = discord.Embed(description="{who}, {response}.".format(
            who=tagged_dname(message.author),
            response="ошибка локализации",
            colour=0xC5934B))
        await client.send_message(message.channel, embed=em)
        return
    em = discord.Embed(colour=int(const["em_color"], 16) + 512)
    if not const or const["is_global"]:
        em.description = locale[lang]["global_not_available"].format(who=tagged_dname(message.author))
        await client.send_message(message.channel, embed=em)
        return
    if not (author == server.owner or any(role.permissions.administrator for role in author.roles)):
        em.description = locale[lang]["global_not_allow_to_use"].format(who=tagged_dname(message.author))
        await client.send_message(message.channel, embed=em)
        return
    try:
        await client.delete_message(message)
    except:
        pass
    if not who:
        em.description = locale[lang]["global_not_mention_on_user"].format(who=clear_name(tagged_dname(message.author))) #{}, введенное значение не является ссылкой на пользователя
        await client.send_message(message.channel, embed=em)
        return
    if who.bot:
        em.description = locale[lang]["global_bot_mentioned"].format(
            who=clear_name(tagged_dname(message.author)),
            bot=clear_name(who.display_name[:50])
        )
        await client.send_message(message.channel, embed=em)
        return
    if not count:
        em.description =locale[lang]["global_not_number"].format(who=clear_name(tagged_dname(message.author))) #{}, введенное значение не является числом.
        await client.send_message(message.channel, embed=em)
        return
    if not const["is_global"]:
        stats_type = message.server.id
    else:
        stats_type = "global"
    dat = await conn.fetchrow("SELECT cash FROM users WHERE stats_type = '{stats_type}' AND discord_id = '{id}'".format(stats_type=stats_type, id=who.id))
    if dat:
        counts = dat["cash"] - count
        if counts < 0:
            counts = 0
        await conn.execute("UPDATE users SET cash = {cash} WHERE stats_type = '{stats_type}' AND discord_id = '{id}'".format(
            cash=counts,
            stats_type=stats_type,
            id=who.id
        ))
    else:
        await conn.execute("INSERT INTO users(name, discord_id, stats_type) VALUES('{}', '{}', '{}')".format(clear_name(who.display_name[:50]), who.id, stats_type))
    em.description = locale[lang]["admin_you_dont_like_him"].format(who.display_name, count, const["server_money"]) #{} не понравился админу. Штраф - {} {}
    await client.send_message(message.channel, embed=em)
    return

async def a_unfriend(client, conn, context, who_id, reason):
    message = context.message
    try:
        await client.delete_message(message)
    except:
        pass
    if not reason:
        reason = 'NULL'
    else:
        reason = "'" + reason + "'"
    dat = await conn.fetchrow("SELECT discord_id FROM black_list_not_ddos WHERE discord_id = '{id}'".format(id=who_id))
    em = discord.Embed(colour=0xC5934B)
    if not who_id:
        em.description = "Неправильно введен ID пользователя."
        await client.send_message(message.channel, embed=em)
        return
    if not dat:
        await conn.execute("INSERT INTO black_list_not_ddos(discord_id, reason) VALUES('{id}', {reason})".format(id=who_id, reason=reason))
        em.description = "ID '{id}' удален из друзей Томори.".format(id=who_id)
    else:
        em.description = "ID '{id}'. Даже слышать ничего не хочу!!! Я не дружу с ним!".format(id=who_id)
    await client.send_message(message.channel, embed=em)

async def a_kick(client, conn, context, who, reason):
    message = context.message
    server = message.server
    server_id = message.server.id
    author = message.author
    const = await get_cached_server(conn, server_id)
    lang = const["locale"]
    if not lang in locale.keys():
        em = discord.Embed(description="{who}, {response}.".format(
            who=tagged_dname(message.author),
            response="ошибка локализации",
            colour=0xC5934B))
        await client.send_message(message.channel, embed=em)
        return
    em = discord.Embed(colour=int(const["em_color"], 16) + 512)
    if not const or not const["is_kick"]:
        em.description = locale[lang]["global_not_available"].format(who=tagged_dname(message.author))
        await client.send_message(message.channel, embed=em)
        return
    try:
        await client.delete_message(message)
    except:
        pass
    if not author == server.owner:
        for role in author.roles:
            if role.permissions.kick_members or role.permissions.administrator:
                break
        else:
            em.description = locale[lang]["global_not_allow_to_use"].format(tagged_dname(message.author))
            await client.send_message(message.channel, embed=em)
            return
    if not who:
        em.description = locale[lang]["global_not_mention_on_user"].format(clear_name(tagged_dname(message.author)))
        await client.send_message(message.channel, embed=em)
        return
    if who == server.owner or any(role.permissions.administrator for role in who.roles):
        em.description = locale[lang]["admin_can_not_kick"].format(who=tagged_dname(message.author))
        await client.send_message(message.channel, embed=em)
        return
    if not reason:
        reason = locale[lang]["admin_no_reason"]
    else:
        res = message.content.split(maxsplit=2)
        reason = res[2]
    try:
        await client.kick(who)
        c_ban = discord.Embed(colour=0xF10118)
        c_ban.set_author(name=locale[lang]["admin_user_kick"], icon_url=server.icon_url)
        c_ban.add_field(
            name=locale[lang]["admin_user"],
            value="{0.mention}".format(who),
            inline=True
        )
        c_ban.add_field(
            name=locale[lang]["admin_moderator"],
            value="{0.mention}".format(message.author),
            inline=True
        )
        c_ban.add_field(
            name=locale[lang]["admin_reason"],
            value="{0}".format(reason),
            inline=True
        )
        c_ban.set_footer(text="ID: {0.id} • {1}".format(who, time.ctime(time.time())))
        if server_id == nazarik_id:
            await client.send_message(client.get_channel(nazarik_log_id), embed=c_ban)
        await client.send_message(message.channel, embed=c_ban)
        return
    except:
        em.description = locale[lang]["admin_didnt_manage_to_kick"].format(clear_name(tagged_dname(message.author)), who.display_name) #{}, не удалось кикнуть {}
        await client.send_message(message.channel, embed=em)
        return

async def a_ban(client, conn, context, who, reason):
    message = context.message
    server = message.server
    server_id = message.server.id
    author = message.author
    const = await get_cached_server(conn, server_id)
    lang = const["locale"]
    if not lang in locale.keys():
        em = discord.Embed(description="{who}, {response}.".format(
            who=tagged_dname(message.author),
            response="ошибка локализации",
            colour=0xC5934B))
        await client.send_message(message.channel, embed=em)
        return
    em = discord.Embed(colour=int(const["em_color"], 16) + 512)
    if not const or not const["is_ban"]:
        em.description = locale[lang]["global_not_available"].format(who=tagged_dname(message.author))
        await client.send_message(message.channel, embed=em)
        return
    try:
        await client.delete_message(message)
    except:
        pass
    if not author == server.owner:
        for role in author.roles:
            if role.permissions.ban_members or role.permissions.administrator:
                break
        else:
            em.description = locale[lang]["global_not_allow_to_use"].format(tagged_dname(message.author))
            await client.send_message(message.channel, embed=em)
            return
    if not who:
        em.description = locale[lang]["global_not_mention_on_user"].format(clear_name(tagged_dname(message.author)))
        await client.send_message(message.channel, embed=em)
        return
    if who == server.owner or any(role.permissions.administrator for role in who.roles):
        em.description = locale[lang]["admin_can_not_ban"].format(who=tagged_dname(message.author))
        await client.send_message(message.channel, embed=em)
        return
    if not reason:
        reason = locale[lang]["admin_no_reason"]
    else:
        res = message.content.split(maxsplit=2)
        reason = res[2]
    try:
        await client.ban(who)
        c_ban = discord.Embed(colour=0xF10118)
        c_ban.set_author(name=locale[lang]["admin_user_ban"], icon_url=server.icon_url)
        c_ban.add_field(
            name=locale[lang]["admin_user"],
            value="{0.mention}".format(who),
            inline=True
        )
        c_ban.add_field(
            name=locale[lang]["admin_moderator"],
            value="{0.mention}".format(message.author),
            inline=True
        )
        c_ban.add_field(
            name=locale[lang]["admin_reason"],
            value="{0}".format(reason),
            inline=True
        )
        c_ban.set_footer(text="ID: {0.id} • {1}".format(who, time.ctime(time.time())))
        if server_id == nazarik_id:
            await client.send_message(client.get_channel(nazarik_log_id), embed=c_ban)
        await client.send_message(message.channel, embed=c_ban)
        return
    except:
        em.description = locale[lang]["admin_didnt_manage_to_ban"].format(clear_name(tagged_dname(message.author)), who.display_name)
        await client.send_message(message.channel, embed=em)
        return

async def a_unban(client, conn, context, name):
    message = context.message
    server = message.server
    server_id = message.server.id
    author = message.author
    const = await get_cached_server(conn, server_id)
    lang = const["locale"]
    if not lang in locale.keys():
        em = discord.Embed(description="{who}, {response}.".format(
            who=tagged_dname(message.author),
            response="ошибка локализации",
            colour=0xC5934B))
        await client.send_message(message.channel, embed=em)
        return
    em = discord.Embed(colour=int(const["em_color"], 16) + 512)
    if not const or not const["is_ban"]:
        em.description = locale[lang]["global_not_available"].format(who=tagged_dname(message.author))
        await client.send_message(message.channel, embed=em)
        return
    try:
        await client.delete_message(message)
    except:
        pass
    if not author == server.owner:
        for role in author.roles:
            if role.permissions.ban_members or role.permissions.administrator:
                break
        else:
            em.description = locale[lang]["global_not_allow_to_use"].format(tagged_dname(message.author))
            await client.send_message(message.channel, embed=em)
            return
    who = None
    bans = await client.get_bans(server)
    if not name:
        return
    who = discord.utils.get(bans, id=name)
    if not who:
        who = discord.utils.get(bans, name=name)
    if not who:
        em.description = locale[lang]["global_not_mention_on_user"].format(clear_name(tagged_dname(message.author)))
        await client.send_message(message.channel, embed=em)
        return
    try:
        await client.unban(server, who)
        c_ban = discord.Embed(colour=0xF10118)
        c_ban.set_author(name=locale[lang]["admin_user_unban"], icon_url=server.icon_url)
        c_ban.add_field(
            name=locale[lang]["admin_user"],
            value="{0.mention}".format(who),
            inline=True
        )
        c_ban.add_field(
            name=locale[lang]["admin_moderator"],
            value="{0.mention}".format(message.author),
            inline=True
        )
        c_ban.set_footer(text="ID: {0.id} • {1}".format(who, time.ctime(time.time())))
        if server_id == nazarik_id:
            await client.send_message(client.get_channel(nazarik_log_id), embed=c_ban)
        await client.send_message(message.channel, embed=c_ban)
        return
    except:
        em.description = locale[lang]["admin_didnt_manage_to_unban"].format(clear_name(message.author.display_name[:50]), who.display_name)
        await client.send_message(message.channel, embed=em)
        return

async def a_mute(client, conn, context, who, reason):
    message = context.message
    server = message.server
    server_id = message.server.id
    author = message.author
    if not reason:
        reason = locale[lang]["admin_no_reason"]
    else:
        res = message.content.split(" ", maxsplit=2)
        reason = res[2]
    mute_time_ = reason.split(" ")
    if len(mute_time_) > 1:
        mute_time = 0
        try:
            mute_time = int(mute_time_[-1])
            reason = reason.rsplit(" ", maxsplit=1)[0]
        except:
            mute_time = 0
        if mute_time < 0:
            mute_time = 0
    const = await get_cached_server(conn, server_id)
    lang = const["locale"]
    if not lang in locale.keys():
        em = discord.Embed(description="{who}, {response}.".format(
            who=tagged_dname(message.author),
            response="ошибка локализации",
            colour=0xC5934B))
        await client.send_message(message.channel, embed=em)
        return
    em = discord.Embed(colour=int(const["em_color"], 16) + 512)
    if not const or not const["is_mute"]:
        em.description = locale[lang]["global_not_available"].format(who=tagged_dname(message.author))
        await client.send_message(message.channel, embed=em)
        return
    try:
        await client.delete_message(message)
    except:
        pass
    if not author == server.owner:
        for role in author.roles:
            if role.permissions.ban_members or role.permissions.administrator or role.permissions.mute_members or role.permissions.deafen_members:
                break
        else:
            em.description = locale[lang]["global_not_allow_to_use"].format(tagged_dname(message.author))
            await client.send_message(message.channel, embed=em)
            return
    member = discord.utils.get(message.server.members, name=who)
    if not member:
        who = re.sub(r'[<@#&!>]+', '', who.lower())
        member = discord.utils.get(message.server.members, id=who)
    if not member:
        em.description = locale[lang]["incorrect_argument"].format(
            who=tagged_dname(message.author),
            arg="user"
        )
        await client.send_message(message.channel, embed=em)
        return
    if member == server.owner or any(role.permissions.administrator for role in member.roles):
        em.description = locale[lang]["admin_can_not_mute"].format(who=tagged_dname(message.author))
        await client.send_message(message.channel, embed=em)
        return
    unmute_time = int(time.time()) + mute_time
    if not const["antispam_role_id"]:
        return
    role = discord.utils.get(server.roles, id=const["antispam_role_id"])
    if not role:
        return
    if role in member.roles:
        em.description = locale[lang]["admin_already_muted"].format(
            who=tagged_dname(message.author),
            user=tagged_dname(member)
        )
        await client.send_message(message.channel, embed=em)
        return
    await client.add_roles(member, role)

    if mute_time > 0:
        user_dat = await conn.fetchrow("SELECT * FROM mods WHERE type = 'muted_users' AND server_id = '{server}' AND name = '{member}'".format(
            server=server.id,
            member=member.id
        ))
        if user_dat:
            return
        user_dat = await conn.fetchrow("INSERT INTO mods(server_id, name, type, condition, value) VALUES('{server}', '{member}', 'muted_users', '{condition}', 'unmute') RETURNING *".format(
            server=server.id,
            member=member.id,
            condition=unmute_time
        ))
        add_muted(client, user_dat)
    hours=str(mute_time//3600)
    minutes=str((mute_time//60)%60)
    seconds=str(mute_time%60)
    c_mute = discord.Embed(colour=0xF10118)
    c_mute.set_author(name=locale[lang]["admin_user_mute"], icon_url=server.icon_url)
    c_mute.add_field(
        name=locale[lang]["admin_user"],
        value="{0.mention}".format(member),
        inline=True
    )
    c_mute.add_field(
        name=locale[lang]["admin_moderator"],
        value="{0.mention}".format(message.author),
        inline=True
    )
    c_mute.add_field(
        name=locale[lang]["admin_time"],
        value=locale[lang]["global_time"].format(
            hours=hours,
            minutes=minutes,
            seconds=seconds
        ) if mute_time > 0 else "∞",
        inline=True
    )
    c_mute.add_field(
        name=locale[lang]["admin_reason"],
        value="{0}".format(reason),
        inline=True
    )
    c_mute.set_footer(text="ID: {0.id} • {1}".format(member, time.ctime(time.time())))
    try:
        channel = client.get_channel(const["mute_log_channel"])
    except:
        pass
    if not channel:
        channel = message.channel

    def is_user_(m):
        return m.author == member
    await asyncio.wait([
        client.purge_from(channel, after=datetime.utcnow()-timedelta(hours=1), check=is_user_),
        client.send_message(channel, embed=c_mute)
    ])
    return

async def a_unmute(client, conn, context, who, reason):
    message = context.message
    server = message.server
    server_id = message.server.id
    author = message.author
    const = await get_cached_server(conn, server_id)
    lang = const["locale"]
    if not lang in locale.keys():
        em = discord.Embed(description="{who}, {response}.".format(
            who=tagged_dname(message.author),
            response="ошибка локализации",
            colour=0xC5934B))
        await client.send_message(message.channel, embed=em)
        return
    em = discord.Embed(colour=int(const["em_color"], 16) + 512)
    if not const or not const["is_mute"]:
        em.description = locale[lang]["global_not_available"].format(who=tagged_dname(message.author))
        await client.send_message(message.channel, embed=em)
        return
    try:
        await client.delete_message(message)
    except:
        pass
    if not author == server.owner:
        for role in author.roles:
            if role.permissions.ban_members or role.permissions.administrator or role.permissions.mute_members or role.permissions.deafen_members:
                break
        else:
            em.description = locale[lang]["global_not_allow_to_use"].format(tagged_dname(message.author))
            await client.send_message(message.channel, embed=em)
            return
    member = discord.utils.get(message.server.members, name=who)
    if not member:
        who = re.sub(r'[<@#&!>]+', '', who.lower())
        member = discord.utils.get(message.server.members, id=who)
    if not member:
        em.description = locale[lang]["incorrect_argument"].format(
            who=tagged_dname(message.author),
            arg="user"
        )
        await client.send_message(message.channel, embed=em)
        return
    if member == server.owner or any(role.permissions.administrator for role in member.roles):
        em.description = locale[lang]["admin_can_not_mute"].format(who=tagged_dname(message.author))
        await client.send_message(message.channel, embed=em)
        return
    if not reason:
        reason = locale[lang]["admin_no_reason"]
    else:
        res = message.content.split(maxsplit=2)
        reason = res[2]
    if not const["antispam_role_id"]:
        return
    role = discord.utils.get(server.roles, id=const["antispam_role_id"])
    if not role:
        return
    if not role in member.roles:
        em.description = locale[lang]["admin_already_werent_mute"].format(
            who=tagged_dname(message.author),
            user=tagged_dname(member)
        )
        await client.send_message(message.channel, embed=em)
        return

    await asyncio.wait([
        client.remove_roles(member, role),
        conn.execute("DELETE FROM mods WHERE type = 'muted_users' AND server_id = '{server}' AND name = '{member}'".format(
            server=server.id,
            member=member.id
        ))
    ])

    c_mute = discord.Embed(colour=0xF10118)
    c_mute.set_author(name=locale[lang]["admin_user_unmute"], icon_url=server.icon_url)
    c_mute.add_field(
        name=locale[lang]["admin_user"],
        value="{0.mention}".format(member),
        inline=True
    )
    c_mute.add_field(
        name=locale[lang]["admin_moderator"],
        value="{0.mention}".format(message.author),
        inline=True
    )
    c_mute.add_field(
        name=locale[lang]["admin_reason"],
        value="{0}".format(reason),
        inline=True
    )
    c_mute.set_footer(text="ID: {0.id} • {1}".format(member, time.ctime(time.time())))
    try:
        channel = client.get_channel(const["mute_log_channel"])
    except:
        pass
    if not channel:
        channel = message.channel
    await client.send_message(channel, embed=c_mute)
    return
