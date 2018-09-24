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
from discord.ext import commands
from cogs.const import *
from cogs.locale import *

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
    await client.send_message(message.author, "Сервер '{} | {}' деактивирован.".format(message.server.name, message.server.id))
    return

async def a_say(client, conn, context):
    message = context.message
    server_id = message.server.id
    const = await conn.fetchrow("SELECT em_color, is_say, locale FROM settings WHERE discord_id = '{}'".format(server_id))
    lang = const[2]
    if not lang in locale.keys():
        em = discord.Embed(description="{who}, {response}.".format(
            who=message.author.display_name+"#"+message.author.discriminator,
            response="ошибка локализации",
            colour=0xC5934B))
        await client.send_message(message.channel, embed=em)
        return
    em = discord.Embed(colour=int(const[0], 16) + int("0x200", 16))
    if not const or not const[1]:
        em.description = locale[lang]["global_not_available"].format(who=message.author.display_name+"#"+message.author.discriminator)
        await client.send_message(message.channel, embed=em)
        return
    try:
        await client.delete_message(message)
    except:
        pass
    await client.send_message(message.channel, message.content[5:])
    return

async def a_say_embed(client, conn, context):
    message = context.message
    server_id = message.server.id
    const = await conn.fetchrow("SELECT em_color, is_say, locale FROM settings WHERE discord_id = '{}'".format(server_id))
    lang = const[2]
    if not lang in locale.keys():
        em = discord.Embed(description="{who}, {response}.".format(
            who=message.author.display_name+"#"+message.author.discriminator,
            response="ошибка локализации",
            colour=0xC5934B))
        await client.send_message(message.channel, embed=em)
        return
    em = discord.Embed(colour=int(const[0], 16) + int("0x200", 16))
    if not const or not const[1]:
        em.description = locale[lang]["global_not_available"].format(who=message.author.display_name+"#"+message.author.discriminator)
        await client.send_message(message.channel, embed=em)
        return
    try:
        await client.delete_message(message)
    except:
        pass
    em = discord.Embed(colour=int(const[0], 16) + int("0x200", 16))
    em.description = message.content[11:]
    await client.send_message(message.channel, embed=em)
    return

async def a_find_user(client, conn, context, member_id):
    em = discord.Embed(colour=0xC5934B)
    channel_id = context.message.channel.id
    servers_count = 0
    em.title = "Servers with {id}".format(id=member_id)
    for server in client.servers:
        member = server.get_member(member_id)
        if member:
            servers_count += 1
            em.add_field(
                name="#"+str(servers_count)+" "+server.name,
                value=server.id,
                inline=True
            )
            # if servers_count == 15:
            #     break
        member = None
    await client.send_message(context.message.channel, embed=em)

async def a_base(client, conn, context):
    message = context.message
    server_id = message.server.id
    const = await conn.fetchrow("SELECT em_color, locale FROM settings WHERE discord_id = '{}'".format(server_id))
    lang = const[1]
    if not lang in locale.keys():
        em = discord.Embed(description="{who}, {response}.".format(
            who=message.author.display_name+"#"+message.author.discriminator,
            response="ошибка локализации",
            colour=0xC5934B))
        await client.send_message(message.channel, embed=em)
        return
    em = discord.Embed(colour=int(const[0], 16) + int("0x200", 16))
    if not const:
        em.description = locale[lang]["global_not_available"].format(who=message.author.display_name+"#"+message.author.discriminator)
        await client.send_message(message.channel, embed=em)
        return
    try:
        await conn.execute(message.content[6:])
        em.description = locale[lang]["admin_request_completed"].format(message.content[6:]) #Запрос '''{}''' успешно выполнен.
    except:
        em.description = locale[lang]["admin_request_failed"].format(message.content[6:]) #Не удалось выполнить запрос '''{}'''
    await client.send_message(message.channel, embed=em)
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
    const = await conn.fetchrow("SELECT em_color, is_clear, locale FROM settings WHERE discord_id = '{}'".format(server_id))
    lang = const[2]
    if not lang in locale.keys():
        em = discord.Embed(description="{who}, {response}.".format(
            who=message.author.display_name+"#"+message.author.discriminator,
            response="ошибка локализации",
            colour=0xC5934B))
        await client.send_message(message.channel, embed=em)
        return
    em = discord.Embed(colour=int(const[0], 16) + int("0x200", 16))
    if not const or not const[1]:
        em.description = locale[lang]["global_not_available"].format(who=message.author.display_name+"#"+message.author.discriminator)
        await client.send_message(message.channel, embed=em)
        return
    if not author == server.owner:# and not author.id in admin_list:
        for role in author.roles:
            if role.permissions.manage_messages or role.permissions.administrator:
                break
        else:
            em.description = locale[lang]["global_not_allowed"].format(author.display_name) #{}, у тебя нет прав
            await client.send_message(message.channel, embed=em)
            return
    if not count:
        em.description = locale[lang]["global_not_number"].format(clear_name(message.author.display_name+"#"+message.author.discriminator)) #{}, введенное значение не является числом.
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
    const = await conn.fetchrow("SELECT em_color, is_take, server_money, locale FROM settings WHERE discord_id = '{}'".format(server_id))
    lang = const[3]
    if not lang in locale.keys():
        em = discord.Embed(description="{who}, {response}.".format(
            who=message.author.display_name+"#"+message.author.discriminator,
            response="ошибка локализации",
            colour=0xC5934B))
        await client.send_message(message.channel, embed=em)
        return
    em = discord.Embed(colour=int(const[0], 16) + int("0x200", 16))
    if not const or not const[1]:
        em.description = locale[lang]["global_not_available"].format(who=message.author.display_name+"#"+message.author.discriminator)
        await client.send_message(message.channel, embed=em)
        return
    try:
        await client.delete_message(message)
    except:
        pass
    em = discord.Embed(colour=int(const[0], 16) + int("0x200", 16))
    if not who:
        em.description =locale[lang]["global_not_display_name_on_user"].format(clear_name(message.author.display_name+"#"+message.author.discriminator)) #{}, введенное значение не является ссылкой на пользователя
        await client.send_message(message.channel, embed=em)
        return
    if who.bot:
        em.description = locale[lang]["global_bot_display_nameed"].format(
            who=clear_name(message.author.display_name+"#"+message.author.discriminator),
            bot=clear_name(who.display_name[:50])
        )
        await client.send_message(message.channel, embed=em)
        return
    if not count:
        em.description =locale[lang]["global_not_number"].format(clear_name(message.author.display_name+"#"+message.author.discriminator)) #{}, введенное значение не является числом.
        await client.send_message(message.channel, embed=em)
        return
    dat = await conn.fetchrow("SELECT cash FROM users WHERE discord_id = '{}'".format(who.id))
    if dat:
        counts = dat[0] - count
        if counts < 0:
            counts = 0
        await conn.execute("UPDATE users SET cash = {} WHERE discord_id = '{}'".format(counts, who.id))
    else:
        await conn.execute("INSERT INTO users(name, discord_id) VALUES('{}', '{}')".format(clear_name(who.display_name[:50]), who.id))
    em.description = locale[lang]["admin_you_dont_like_him"].format(who.display_name, count, const[2]) #{} не понравился админу. Штраф - {} {}
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
    const = await conn.fetchrow("SELECT em_color, is_kick, locale FROM settings WHERE discord_id = '{}'".format(server_id))
    lang = const[2]
    if not lang in locale.keys():
        em = discord.Embed(description="{who}, {response}.".format(
            who=message.author.display_name+"#"+message.author.discriminator,
            response="ошибка локализации",
            colour=0xC5934B))
        await client.send_message(message.channel, embed=em)
        return
    em = discord.Embed(colour=int(const[0], 16) + int("0x200", 16))
    if not const or not const[1]:
        em.description = locale[lang]["global_not_available"].format(who=message.author.display_name+"#"+message.author.discriminator)
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
            em.description = locale[lang]["global_not_allowed"].format(author.display_name)
            await client.send_message(message.channel, embed=em)
            return
    if not who:
        em.description = locale[lang]["global_not_display_name_on_user"].format(clear_name(message.author.display_name+"#"+message.author.discriminator))
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
            value="{0.display_name}".format(who),
            inline=True
        )
        c_ban.add_field(
            name=locale[lang]["admin_moderator"],
            value="{0.display_name}".format(message.author),
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
        em.description = locale[lang]["admin_didnt_manage_to_kick"].format(clear_name(message.author.display_name+"#"+message.author.discriminator), who.display_name) #{}, не удалось кикнуть {}
        await client.send_message(message.channel, embed=em)
        return

async def a_ban(client, conn, context, who, reason):
    message = context.message
    server = message.server
    server_id = message.server.id
    author = message.author
    const = await conn.fetchrow("SELECT em_color, is_kick, locale FROM settings WHERE discord_id = '{}'".format(server_id))
    lang = const[2]
    if not lang in locale.keys():
        em = discord.Embed(description="{who}, {response}.".format(
            who=message.author.display_name+"#"+message.author.discriminator,
            response="ошибка локализации",
            colour=0xC5934B))
        await client.send_message(message.channel, embed=em)
        return
    em = discord.Embed(colour=int(const[0], 16) + int("0x200", 16))
    if not const or not const[1]:
        em.description = locale[lang]["global_not_available"].format(who=message.author.display_name+"#"+message.author.discriminator)
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
            em.description = locale[lang]["global_not_allowed"].format(author.display_name)
            await client.send_message(message.channel, embed=em)
            return
    if not who:
        em.description = locale[lang]["global_not_display_name_on_user"].format(clear_name(message.author.display_name+"#"+message.author.discriminator))
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
            value="{0.display_name}".format(who),
            inline=True
        )
        c_ban.add_field(
            name=locale[lang]["admin_moderator"],
            value="{0.display_name}".format(message.author),
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
        em.description = locale[lang]["admin_didnt_manage_to_ban"].format(clear_name(message.author.display_name+"#"+message.author.discriminator), who.display_name)
        await client.send_message(message.channel, embed=em)
        return

async def a_unban(client, conn, context, whos, reason):
    message = context.message
    server = message.server
    server_id = message.server.id
    author = message.author
    const = await conn.fetchrow("SELECT em_color, is_kick, locale FROM settings WHERE discord_id = '{}'".format(server_id))
    lang = const[2]
    if not lang in locale.keys():
        em = discord.Embed(description="{who}, {response}.".format(
            who=message.author.display_name+"#"+message.author.discriminator,
            response="ошибка локализации",
            colour=0xC5934B))
        await client.send_message(message.channel, embed=em)
        return
    em = discord.Embed(colour=int(const[0], 16) + int("0x200", 16))
    if not const or not const[1]:
        em.description = locale[lang]["global_not_available"].format(who=message.author.display_name+"#"+message.author.discriminator)
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
            em.description = locale[lang]["global_not_allowed"].format(author.display_name)
            await client.send_message(message.channel, embed=em)
            return
    who = None
    bans = await client.get_bans(server)
    if not whos:
        return
    for s in bans:
        if s.id == whos:
            who = s
            break
    if not who:
        em.description = locale[lang]["global_not_display_name_on_user"].format(clear_name(message.author.display_name+"#"+message.author.discriminator))
        await client.send_message(message.channel, embed=em)
        return
    if not reason:
        reason = locale[lang]["admin_no_reason"]
    else:
        res = message.content.split(maxsplit=2)
        reason = res[2]
    try:
        await client.unban(server, who)
        c_ban = discord.Embed(colour=0xF10118)
        c_ban.set_author(name=locale[lang]["admin_user_unban"], icon_url=server.icon_url)
        c_ban.add_field(
            name=locale[lang]["admin_user"],
            value="{0.display_name}".format(who),
            inline=True
        )
        c_ban.add_field(
            name=locale[lang]["admin_moderator"],
            value="{0.display_name}".format(message.author),
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
        em.description = locale[lang]["admin_didnt_manage_to_unban"].format(clear_name(message.author.display_name[:50]), who.display_name)
        await client.send_message(message.channel, embed=em)
        return
