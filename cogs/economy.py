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

async def e_timely(client, conn, context):
    message = context.message
    server_id = message.server.id
    dat = await conn.fetchrow("SELECT cash, daily_time FROM users WHERE discord_id = '{discord_id}'".format(discord_id=message.author.id))
    const = await conn.fetchrow("SELECT server_money, daily_count, daily_cooldown, em_color, is_timely, locale, likes FROM settings WHERE discord_id = '{discord_id}'".format(discord_id=server_id))
    lang = const["locale"]
    if not lang in locale.keys():
        em = discord.Embed(description="{who}, {response}.".format(
            who=message.author.display_name+"#"+message.author.discriminator,
            response="ошибка локализации",
            colour=0xC5934B))
        await client.send_message(message.channel, embed=em)
        return
    em = discord.Embed(colour=int(const["em_color"], 16) + 512)
    if not const or not const["is_timely"]:
        em.description = locale[lang]["global_not_available"].format(who=message.author.display_name+"#"+message.author.discriminator)
        await client.send_message(message.channel, embed=em)
        return
    try:
        await client.delete_message(message)
    except:
        pass
    count = const["daily_count"]
    global top_servers
    top_servers = await conn.fetch("SELECT discord_id FROM settings ORDER BY likes DESC, like_time ASC LIMIT 10")
    if any(server_id == server["discord_id"] for server in top_servers):
        count *= 2
    if dat:
        tim = int(time.time()) - dat["daily_time"]
        if tim < const["daily_cooldown"]:
            t=const["daily_cooldown"] - tim
            h=str(t//3600)
            m=str((t//60)%60)
            s=str(t%60)
            em.description = "{later1}\n{later2}".format(
            later1=locale[lang]["economy_try_again_later1"].format(
                who=clear_name(message.author.display_name+"#"+message.author.discriminator),
                money=const["server_money"]
                ),
            later2=locale[lang]["economy_try_again_later2"].format(
                hours=h,
                minutes=m,
                seconds=s
                )
            )
            em.add_field(
                name="Поддержать Томори",
                value=tomori_links,
                inline=False
            )
            await client.send_message(message.channel, embed=em)
        else:
            await conn.execute("UPDATE users SET cash = {cash}, daily_time = {time} WHERE discord_id = '{discord_id}'".format(cash=dat["cash"] + count, time=int(time.time()), discord_id=message.author.id))
            em.description = locale[lang]["economy_received_money"].format(clear_name(message.author.display_name+"#"+message.author.discriminator), count, const[0])
            await client.send_message(message.channel, embed=em)
    else:
        await conn.execute("INSERT INTO users(name, discord_id, cash, daily_time) VALUES('{}', '{}', {}, {})".format(clear_name(message.author.display_name[:50]), message.author.id, count, int(time.time())))
        em.description = locale[lang]["economy_received_money"].format(clear_name(message.author.display_name+"#"+message.author.discriminator), count, const[0])
        await client.send_message(message.channel, embed=em)
    return

async def e_give(client, conn, context, who, count):
    message = context.message
    server_id = message.server.id
    const = await conn.fetchrow("SELECT server_money, server_money_name_net, em_color, is_give, locale FROM settings WHERE discord_id = '{}'".format(server_id))
    lang = const[4]
    if not lang in locale.keys():
        em = discord.Embed(description="{who}, {response}.".format(
            who=message.author.display_name+"#"+message.author.discriminator,
            response="ошибка локализации",
            colour=0xC5934B))
        await client.send_message(message.channel, embed=em)
        return
    em = discord.Embed(colour=int(const[2], 16) + 512)
    if not const or not const[3]:
        em.description = locale[lang]["global_not_available"].format(who=message.author.display_name+"#"+message.author.discriminator)
        await client.send_message(message.channel, embed=em)
        return
    try:
        await client.delete_message(message)
    except:
        pass
    if not who:
        em.description = locale[lang]["global_not_display_name_on_user"].format(clear_name(message.author.display_name+"#"+message.author.discriminator))
        await client.send_message(message.channel, embed=em)
        return
    if who.bot:
        em.description = locale[lang]["global_bot_display_nameed"].format(
            who=clear_name(message.author.display_name+"#"+message.author.discriminator),
            bot=clear_name(who.display_name[:50])
        )
        await client.send_message(message.channel, embed=em)
        return
    if who.id == message.author.id:
        em.description =locale[lang]["global_choose_someone_else"].format(clear_name(message.author.display_name+"#"+message.author.discriminator))
        await client.send_message(message.channel, embed=em)
        return
    if not count.isdigit() and not count == 'all':
        em.description = locale[lang]["global_not_number"].format(clear_name(message.author.display_name+"#"+message.author.discriminator))
        await client.send_message(message.channel, embed=em)
        return
    if count == '0':
        em.description = locale[lang]["economy_cant_give_zero"].format(clear_name(message.author.display_name+"#"+message.author.discriminator))
        await client.send_message(message.channel, embed=em)
        return
    count = count[:20]
    dat = await conn.fetchrow("SELECT cash FROM users WHERE discord_id = '{}'".format(message.author.id))
    dates = await conn.fetchrow("SELECT cash FROM users WHERE discord_id = '{}'".format(who.id))
    if not dates:
        await conn.execute("INSERT INTO users(name, discord_id) VALUES('{}', '{}')".format(clear_name(who.display_name[:50]), who.id))
        dates = await conn.fetchrow("SELECT cash FROM users WHERE discord_id = '{}'".format(who.id))
    if dat:
        if count == 'all':
            cooks = dat[0]
        elif dat[0] < int(count):
            em.description = locale[lang]["global_dont_have_that_much_money"].format(who=message.author.display_name+"#"+message.author.discriminator, money=const[1])
            em.add_field(
                name="Поддержать Томори",
                value=tomori_links,
                inline=False
            )
            await client.send_message(message.channel, embed=em)
            return
        else:
            cooks = int(count)
        await conn.execute("UPDATE users SET cash = {} WHERE discord_id = '{}'".format(str(dat[0] - cooks), message.author.id))
        await conn.execute("UPDATE users SET cash = {} WHERE discord_id = '{}'".format(str(dates[0] + cooks), who.id))
        em.description = locale[lang]["economy_gift"].format(clear_name(message.author.display_name+"#"+message.author.discriminator), cooks, const[0], clear_name(who.display_name[:50]))
    else:
        await conn.execute("INSERT INTO users(name, discord_id) VALUES('{}', '{}')".format(clear_name(message.author.display_name[:50]), message.author.id))
        em.description = locale[lang]["global_dont_have_that_much_money"].format(who=message.author.display_name+"#"+message.author.discriminator, money=const[1])
        em.add_field(
            name="Поддержать Томори",
            value=tomori_links,
            inline=False
        )
    await client.send_message(message.channel, embed=em)
    return

async def e_cash(client, conn, context):
    message = context.message
    server_id = message.server.id
    const = await conn.fetchrow("SELECT server_money, em_color, is_cash, locale FROM settings WHERE discord_id = '{}'".format(server_id))
    lang = const[3]
    if not lang in locale.keys():
        em = discord.Embed(description="{who}, {response}.".format(
            who=message.author.display_name+"#"+message.author.discriminator,
            response="ошибка локализации",
            colour=0xC5934B))
        await client.send_message(message.channel, embed=em)
        return
    em = discord.Embed(colour=int(const[1], 16) + 512)
    if not const or not const[2]:
        em.description = locale[lang]["global_not_available"].format(who=message.author.display_name+"#"+message.author.discriminator)
        await client.send_message(message.channel, embed=em)
        return
    try:
        await client.delete_message(message)
    except:
        pass
    dat = await conn.fetchrow("SELECT cash FROM users WHERE discord_id = '{}'".format(message.author.id))
    if dat:
        count = dat[0]
    else:
        count = 0
    em.description = locale[lang]["economy_user_have"].format(clear_name(message.author.display_name+"#"+message.author.discriminator), count, const[0])
    await client.send_message(message.channel, embed=em)
    return

async def e_top(client, conn, context):
    message = context.message
    server_id = message.server.id
    const = await conn.fetchrow("SELECT server_money, em_color, is_top, locale FROM settings WHERE discord_id = '{}'".format(server_id))
    lang = const["locale"]
    if not lang in locale.keys():
        em = discord.Embed(description="{who}, {response}.".format(
            who=message.author.display_name+"#"+message.author.discriminator,
            response="ошибка локализации",
            colour=0xC5934B))
        await client.send_message(message.channel, embed=em)
        return
    _locale = locale[lang]
    em = discord.Embed(colour=int(const["em_color"], 16) + 512)
    if not const or not const["is_top"]:
        em.description = _locale["global_not_available"].format(who=message.author.display_name+"#"+message.author.discriminator)
        await client.send_message(message.channel, embed=em)
        return
    try:
        await client.delete_message(message)
    except:
        pass
    em.title = _locale["economy_top_of_users"]
    dat = await conn.fetchrow("SELECT COUNT(name) FROM users")
    if dat[0] == 0:
        em.description = _locale["global_list_is_empty"]
        await client.send_message(message.channel, embed=em)
        return
    dat = await conn.fetch("SELECT name, xp_count, discriminator FROM users ORDER BY xp_count DESC LIMIT 10")
    for index, user in enumerate(dat):
        xp_lvl = 0
        if user["xp_count"] > 0:
            while user["xp_count"] >= (xp_lvl * (xp_lvl + 1) * 5):
                xp_lvl = xp_lvl + 1
        if not xp_lvl == 0:
            xp_lvl -= 1
        em.add_field(
            name="#{index} {name}#{discriminator}".format(
                index=index+1,
                name=user["name"],
                discriminator=user["discriminator"]
            ),
            value=_locale["economy_top_element"].format(
                lvl=xp_lvl,
                xp_count=user["xp_count"]
            ),
            inline=False
        )
    await client.send_message(message.channel, embed=em)
    return

async def e_work(client, conn, context):
    message = context.message
    server_id = message.server.id
    const = await conn.fetchrow("SELECT em_color, is_work, locale FROM settings WHERE discord_id = '{}'".format(server_id))
    lang = const[2]
    if not lang in locale.keys():
        em = discord.Embed(description="{who}, {response}.".format(
            who=message.author.display_name+"#"+message.author.discriminator,
            response="ошибка локализации",
            colour=0xC5934B))
        await client.send_message(message.channel, embed=em)
        return
    em = discord.Embed(colour=int(const[0], 16) + 512)
    if not const or not const[1]:
        em.description = locale[lang]["global_not_available"].format(who=message.author.display_name+"#"+message.author.discriminator)
        await client.send_message(message.channel, embed=em)
        return
    try:
        await client.delete_message(message)
    except:
        pass
    dat = await conn.fetchrow("SELECT work_time FROM users WHERE discord_id = '{}'".format(message.author.id))
    if dat:
        if dat[0] == 0:
            await conn.execute("UPDATE users SET work_time = {} WHERE discord_id = '{}'".format(int(time.time()), message.author.id))
            em.description = locale[lang]["economy_went_to_work"].format(clear_name(message.author.display_name+"#"+message.author.discriminator))
            await client.send_message(message.channel, embed=em)
        else:
            em.description = locale[lang]["economy_already_at_work"].format(clear_name(message.author.display_name+"#"+message.author.discriminator))
            em.add_field(
                name="Поддержать Томори",
                value=tomori_links,
                inline=False
            )
            await client.send_message(message.channel, embed=em)
    else:
        await conn.execute("INSERT INTO users(name, discord_id, work_time) VALUES('{}', '{}', {})".format(clear_name(message.author.display_name[:50]), message.author.id, int(time.time())))
        em.description = locale[lang]["economy_went_to_work"].format(clear_name(message.author.display_name+"#"+message.author.discriminator))
        await client.send_message(message.channel, embed=em)
    return

async def e_br(client, conn, context, count):
    message = context.message
    server_id = message.server.id
    const = await conn.fetchrow("SELECT server_money, em_color, is_br, locale FROM settings WHERE discord_id = '{}'".format(server_id))
    lang = const[3]
    if not lang in locale.keys():
        em = discord.Embed(description="{who}, {response}.".format(
            who=message.author.display_name+"#"+message.author.discriminator,
            response="ошибка локализации",
            colour=0xC5934B))
        await client.send_message(message.channel, embed=em)
        return
    em = discord.Embed(colour=int(const[1], 16) + 512)
    if not const or not const[2]:
        em.description = locale[lang]["global_not_available"].format(who=message.author.display_name+"#"+message.author.discriminator)
        await client.send_message(message.channel, embed=em)
        return
    try:
        await client.delete_message(message)
    except:
        pass
    if not count or not count.isdigit() and not count == 'all':
        em.description = locale[lang]["global_not_number"].format(clear_name(message.author.display_name+"#"+message.author.discriminator))
        await client.send_message(message.channel, embed=em)
        return
    if count == '0':
        em.description = locale[lang]["economy_cant_put_bet_of_zero"].format(clear_name(message.author.display_name+"#"+message.author.discriminator))
        await client.send_message(message.channel, embed=em)
        return
    count = count[:20]
    dat = await conn.fetchrow("SELECT cash FROM users WHERE discord_id = '{}'".format(message.author.id))
    if dat:
        if count == 'all':
            summ = dat[0]
        elif dat[0] < int(count):
            em.description = locale[lang]["global_dont_have_that_much_money"].format(who=message.author.display_name+"#"+message.author.discriminator, money=const[0])
            em.add_field(
                name="Поддержать Томори",
                value=tomori_links,
                inline=False
            )
            await client.send_message(message.channel, embed=em)
            return
        else:
            summ = int(count)
        if summ > 5000:
            em.description = locale[lang]["economy_max_bet_is_5000"].format(clear_name(message.author.display_name+"#"+message.author.discriminator), const[0])
            await client.send_message(message.channel, embed=em)
            return
        if summ == 0:
            em.description = locale[lang]["economy_cant_put_bet_of_zero"].format(clear_name(message.author.display_name+"#"+message.author.discriminator))
            await client.send_message(message.channel, embed=em)
            return
        if (random.randint(0, 99)) > 49:
            await conn.execute("UPDATE users SET cash = {} WHERE discord_id = '{}'".format(dat[0] + summ, message.author.id))
            em.description = locale[lang]["economy_you_win"].format(clear_name(message.author.display_name+"#"+message.author.discriminator), summ, const[0])
            await client.send_message(message.channel, embed=em)
        else:
            await conn.execute("UPDATE users SET cash = {} WHERE discord_id = '{}'".format(dat[0] - summ, message.author.id))
            em.description = locale[lang]["economy_you_lose"].format(clear_name(message.author.display_name+"#"+message.author.discriminator), summ, const[0])
            await client.send_message(message.channel, embed=em)
    else:
        await conn.execute("INSERT INTO users(name, discord_id) VALUES('{}', '{}')".format(clear_name(message.author.display_name[:50]), message.author.id))
        em.description = locale[lang]["global_dont_have_that_much_money"].format(who=message.author.display_name+"#"+message.author.discriminator, money=const[0])
        em.add_field(
            name="Поддержать Томори",
            value=tomori_links,
            inline=False
        )
        await client.send_message(message.channel, embed=em)
    return

async def e_slots(client, conn, context, count):
    message = context.message
    server_id = message.server.id
    const = await conn.fetchrow("SELECT server_money, em_color, is_slots, locale FROM settings WHERE discord_id = '{}'".format(server_id))
    lang = const[3]
    if not lang in locale.keys():
        em = discord.Embed(description="{who}, {response}.".format(
            who=message.author.display_name+"#"+message.author.discriminator,
            response="ошибка локализации",
            colour=0xC5934B))
        await client.send_message(message.channel, embed=em)
        return
    em = discord.Embed(colour=int(const[1], 16) + 512)
    if not const or not const[2]:
        em.description = locale[lang]["global_not_available"].format(who=message.author.display_name+"#"+message.author.discriminator)
        await client.send_message(message.channel, embed=em)
        return
    try:
        await client.delete_message(message)
    except:
        pass
    if not count or not count.isdigit() and not count == 'all':
        em.description = locale[lang]["global_not_number"].format(clear_name(message.author.display_name+"#"+message.author.discriminator))
        await client.send_message(message.channel, embed=em)
        return
    if count == '0':
        em.description = locale[lang]["economy_cant_put_bet_of_zero"].format(clear_name(message.author.display_name+"#"+message.author.discriminator))
        await client.send_message(message.channel, embed=em)
        return
    count = count[:20]
    dat = await conn.fetchrow("SELECT cash, name FROM users WHERE discord_id = '{}'".format(message.author.id))
    em.set_author(name=locale[lang]["economy_slots"].format(dat[1]), icon_url=message.author.avatar_url)
    if dat:
        if count == 'all':
            summ = dat[0]
        elif dat[0] < int(count):
            em.description = locale[lang]["global_dont_have_that_much_money"].format(who=message.author.display_name+"#"+message.author.discriminator, money=const[0])
            em.add_field(
                name="Поддержать Томори",
                value=tomori_links,
                inline=False
            )
            await client.send_message(message.channel, embed=em)
            return
        else:
            summ = int(count)
        if summ > 1000:
            em.description = locale[lang]["economy_max_bet_is_1000"].format(clear_name(message.author.display_name+"#"+message.author.discriminator), const[0])
            await client.send_message(message.channel, embed=em)
            return
        if summ == 0:
            em.description = locale[lang]["economy_cant_put_bet_of_zero"].format(clear_name(message.author.display_name+"#"+message.author.discriminator))
            await client.send_message(message.channel, embed=em)
            return
        random.shuffle(slots_ver)
        fails = 0
        rets = 0
        if slots_ver[0] == slot_trap or slots_ver[1] == slot_trap or slots_ver[2] == slot_trap:
            fails = 5
        else:
            if slots_ver[0] == slot_boom or slots_ver[0] == slot_melban:
                fails += 1
            if slots_ver[1] == slot_boom or slots_ver[1] == slot_melban:
                fails += 1
            if slots_ver[2] == slot_boom or slots_ver[2] == slot_melban:
                fails += 1
        if fails < 2:
            i = -1
            while i < 2:
                i += 1
                if slots_ver[i] == slot_kanna:
                    rets += summ * 5
                    continue
                if slots_ver[i] == slot_awoo:
                    rets += summ
                    continue
                if slots_ver[i] == slot_salt:
                    rets += int(summ / 2)
                    continue
                if slots_ver[i] == slot_doge:
                    rets += int(summ + summ / 2)
                    continue
                if slots_ver[i] == slot_pantsu2:
                    rets += summ * 2
                    continue
                if slots_ver[i] == slot_pantsu1:
                    rets += summ * 3
                    continue
            await conn.execute("UPDATE users SET cash = {} WHERE discord_id = '{}'".format(dat[0] + rets, message.author.id))
            em.description = " {slot1} {slot2} {slot3}\n{response}".format(
                slot1=slots_ver[0],
                slot2=slots_ver[1],
                slot3=slots_ver[2],
                response=locale[lang]["economy_you_win"].format(clear_name(message.author.display_name+"#"+message.author.discriminator), rets, const[0])
            )
        else:
            await conn.execute("UPDATE users SET cash = {} WHERE discord_id = '{}'".format(dat[0] - summ, message.author.id))
            em.description = " {slot1} {slot2} {slot3}\n{response}".format(
                slot1=slots_ver[0],
                slot2=slots_ver[1],
                slot3=slots_ver[2],
                response=locale[lang]["economy_you_lose"].format(clear_name(message.author.display_name+"#"+message.author.discriminator), summ, const[0])
            )
    else:
        await conn.execute("INSERT INTO users(name, discord_id) VALUES('{}', '{}')".format(clear_name(message.author.display_name[:50]), message.author.id))
        em.description = locale[lang]["global_dont_have_that_much_money"].format(who=message.author.display_name+"#"+message.author.discriminator, money=const[0])
        em.add_field(
            name="Поддержать Томори",
            value=tomori_links,
            inline=False
        )
    await client.send_message(message.channel, embed=em)
    return
