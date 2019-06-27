import os
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
import imghdr
from discord.ext import commands
from config.settings import settings

from PIL import Image, ImageChops, ImageFont, ImageDraw, ImageSequence, ImageFilter, GifImagePlugin
from PIL.GifImagePlugin import getheader, getdata
from functools import partial

import aiohttp
from io import BytesIO
from typing import Union
from cogs.const import *
from cogs.ids import *
from cogs.util import *
from cogs.locale import *
from config.constants import *


mask = Image.new('L', (1000, 1000), 0)
draws = ImageDraw.Draw(mask)
draws.ellipse((0, 0) + (1000, 1000), fill=255)
mask = mask.resize((200, 200), Image.ANTIALIAS)

mask_gif = Image.new('L', (1000, 1000), 0)
draws = ImageDraw.Draw(mask_gif)
draws.ellipse((0, 0) + (1000, 1000), fill=255)
# mask_gif = mask_gif.resize((200, 200), Image.ANTIALIAS)

mask_profile = Image.new('L', (800, 800), 0)
draws_profile = ImageDraw.Draw(mask_profile)
draws_profile.rectangle((0, 295) + (800, 505), fill=77)
mask_profile = mask_profile.resize((800, 800), Image.ANTIALIAS)

mask_top = Image.new('L', (269, 269), 0)
draws_top = ImageDraw.Draw(mask_top)
draws_top.ellipse((0, 0) + (269, 269), fill=255)
mask_top = mask_top.resize((269, 269), Image.ANTIALIAS)

mask_top_back = Image.new('L', (549, 549), 0)
draws_top_back = ImageDraw.Draw(mask_top_back)
draws_top_back.rectangle((274, 0) + (474, 549), fill=255)
mask_top_back = mask_top_back.resize((549, 549), Image.ANTIALIAS)



async def f_me(client, conn, context, who):
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
    if not const or not const["is_me"]:
        em.description = locale[lang]["global_not_available"].format(who=message.author.display_name+"#"+message.author.discriminator)
        await client.send_message(message.channel, embed=em)
        return
    try:
        await client.delete_message(message)
    except:
        pass
    if not who:
        who = message.author
    if who.bot:
        em.description = locale[lang]["global_bot_mentioned"].format(
            who=message.author.display_name+"#"+message.author.discriminator,
            bot=who.display_name
        )
        await client.send_message(message.channel, embed=em)
        return
    await client.send_typing(message.channel)
    if not const["is_global"]:
        stats_type = message.server.id
    else:
        stats_type = "global"
    dat = await conn.fetchrow("SELECT * FROM users WHERE stats_type = '{stats_type}' AND discord_id = '{id}'".format(stats_type=stats_type, id=who.id))
    if not dat:
        await conn.execute("INSERT INTO users(name, discord_id, stats_type) VALUES('{}', '{}', '{}')".format(clear_name(who.display_name[:50]), who.id, stats_type))
        dat = await conn.fetchrow("SELECT * FROM users WHERE stats_type = '{stats_type}' AND discord_id = '{id}'".format(stats_type=stats_type, id=who.id))
    # cash_rank = await conn.fetchrow("SELECT COUNT(DISTINCT cash) AS qty FROM users WHERE stats_type = '{}' AND cash > {}".format(stats_type, dat["cash"]))
    # xp_rank = await conn.fetchrow("SELECT COUNT(DISTINCT xp_count) AS qty FROM users WHERE stats_type = '{}' AND xp_count > {}".format(stats_type, dat["xp_count"]))
    badges = await conn.fetchrow("SELECT arguments FROM mods WHERE type = 'badges' AND name = '{user}'".format(user=who.id))
#================================================== stats 1
    xp_lvl = 0
    i = 1
    if dat["xp_count"] > 0:
        while dat["xp_count"] >= (i * (i + 1) * 5):
            xp_lvl = xp_lvl + 1
            i = i + 1
    xp_count = str(dat["xp_count"])
    xp_nex_lvl = "/"+str((xp_lvl + 1) * (xp_lvl + 2) * 5)
#==================================================
    img = Image.open("cogs/stat/backgrounds/profile.png")
    draw = ImageDraw.Draw(img)


    ava_url = dat["gif_avatar"]
    if ava_url:
        try:
            response = str(requests.session().get(ava_url).content)
            if not response[2:-1]:
                ava_url = None
        except:
            ava_url = None
    if not ava_url:
        ava_url = who.avatar_url
        if ava_url:
            try:
                response = str(requests.session().get(ava_url).content)
                if not response[2:-1]:
                    ava_url = None
            except:
                ava_url = None
        if not ava_url:
            ava_url = who.default_avatar_url
    ava_url = beauty_icon(ava_url, None)
    response = requests.get(ava_url)
    try:
        avatar = Image.open(BytesIO(response.content))
    except:
        em.description = locale[lang]["global_url_not_image"].format(
            who=message.author.display_name+"#"+message.author.discriminator
        )
        await client.send_message(message.channel, embed=em)
        return

    def handle_image(img):
        back = avatar.convert('RGB').resize((800, 800))
        back = back.filter(ImageFilter.GaussianBlur(5))
        back.putalpha(mask_profile)
        img.paste(back, (0, -295), back)
        draw = ImageDraw.Draw(img)
        if badges and badges["arguments"]:
            shift = 0
            for badge in badges_list:
                if badge in badges["arguments"]:
                    icon = badges_obj.get(badge)
                    if icon:
                        img.paste(icon, (260+shift, 90), icon)
                        shift += 36


        name = u"{}".format(who.display_name+"#"+who.discriminator)
        name_size = 1
        font_name = ImageFont.truetype("cogs/stat/ProximaNova-Bold.otf", name_size)
        while font_name.getsize(name)[0] < 450:
            name_size += 1
            font_name = ImageFont.truetype("cogs/stat/ProximaNova-Bold.otf", name_size)
            if name_size == 50:
                break
        name_size -= 1
        font_name = ImageFont.truetype("cogs/stat/ProximaNova-Bold.otf", name_size)
        draw.text(
            (258, 70-font_name.getsize(name)[1]),
            name,
            (255, 255, 255),
            font=font_name
        )

        t=dat["voice_time"]
        hours=str(t//3600)
        minutes=str((t//60)%60)
        seconds=str(t%60)
        messages = dat["messages"]
        if messages > 50000:
            messages = "50000+"
        stats = "{messages}sms | {h}h {m}m {s}s voice".format(
            messages=messages,
            h=hours,
            m=minutes,
            s=seconds
        )
        font_stats = ImageFont.truetype("cogs/stat/ProximaNova-Regular.ttf", 30)
        draw.text(
            (258, 148),
            stats,
            (255, 255, 255),
            font=font_stats
        )

        down_name = "LVL:\nXP:\nBALANCE:"
        font_down_name = ImageFont.truetype("cogs/stat/ProximaNova-Bold.otf", 33)
        draw.text(
            (24, 221),
            down_name,
            (255, 255, 255),
            font=font_down_name
        )

        font_down = ImageFont.truetype("cogs/stat/ProximaNova-Regular.ttf", 33)
        font_down_xp = ImageFont.truetype("cogs/stat/ProximaNova-Regular.ttf", 17)
        draw.text(
            (95, 221),
            str(xp_lvl),
            (255, 255, 255),
            font=font_down
        )
        draw.text(
            (80, 256),
            str(xp_count),
            (255, 255, 255),
            font=font_down
        )
        draw.text(
            (80+font_down.getsize(str(xp_count))[0], 270),
            str(xp_nex_lvl),
            (255, 255, 255),
            font=font_down_xp
        )
        draw.text(
            (187, 292),
            str(dat["cash"]),
            (255, 255, 255),
            font=font_down
        )
        draw.text(
            (187+font_down.getsize(str(dat["cash"]))[0], 306),
            "$",
            (255, 255, 255),
            font=font_down_xp
        )

    filename = 'cogs/stat/return/{}'.format(message.author.id)+ava_url.rsplit("/")[-1]
    if filename.lower().endswith(".gif") and not (badges and any(badge.lower() in badges["arguments"] for badge in ["Nitro", "Partner"])):
        filename = filename[:-4]+".png"

    if filename.endswith(".gif"):

        def iter_frames(im):
            try:
                i= 0
                while 1:
                    im.seek(i)
                    imframe = im.copy()
                    yield imframe
                    i += 1
            except EOFError:
                pass

        images = []
        durations = []
        for frame in iter_frames(avatar):
            durations.append(frame.info['duration'])
            frame = frame.convert('RGBA').resize((1000, 1000))
            frame.putalpha(mask_gif)
            frame = frame.resize((200, 200))
            img_ = img.copy()
            handle_image(img_)
            img_.paste(frame, (24, 5), frame)
            images.append(img_)
        images[0].save(filename, save_all=True, append_images=images[1:], duration=int(sum(durations) / len(durations)), loop=0)
    else:
        handle_image(img)
        avatar = avatar.resize((200, 200)).convert('RGB')
        avatar.putalpha(mask)
        img.paste(avatar, (24, 5), avatar)
        img.save(filename, "PNG")

    try:
        await client.send_file(message.channel, filename)
    except:
        os.remove(filename)
        filename = filename+".png"
        images[0].save(filename)
        await client.send_file(message.channel, filename)
    os.remove(filename)
    return

async def f_hug(client, conn, context, who):
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
    if not const or not const["is_hug"]:
        em.description = locale[lang]["global_not_available"].format(who=message.author.display_name+"#"+message.author.discriminator)
        await client.send_message(message.channel, embed=em)
        return
    try:
        await client.delete_message(message)
    except:
        pass
    if await are_you_nitty(client, lang, who, message):
        return
    if not const["is_global"]:
        stats_type = message.server.id
    else:
        stats_type = "global"
    dat = await conn.fetchrow("SELECT cash FROM users WHERE stats_type = '{stats_type}' AND discord_id = '{id}'".format(stats_type=stats_type, id=message.author.id))
    dates = await conn.fetchrow("SELECT hug_count FROM users WHERE stats_type = '{stats_type}' AND discord_id = '{id}'".format(stats_type=stats_type, id=who.id))
    if not dates:
        await conn.execute("INSERT INTO users(name, discord_id, stats_type) VALUES('{}', '{}', '{}')".format(clear_name(who.display_name[:50]), who.id, stats_type))
        dates = await conn.fetchrow("SELECT hug_count FROM users WHERE stats_type = '{stats_type}' AND discord_id = '{id}'".format(stats_type=stats_type, id=who.id))
    if dat:
        if (const["hug_price"] > dat["cash"]):
            em.description =  locale[lang]["global_dont_have_that_much_money"].format(who=message.author.display_name+"#"+message.author.discriminator, money=const["server_money"])
            if not message.server.id in servers_without_follow_us:
                em = await add_follow_links(client, message, const, em)
        else:
            await conn.execute("UPDATE users SET cash = {cash} WHERE stats_type = '{stats_type}' AND discord_id = '{id}'".format(cash=dat["cash"] - const["hug_price"], stats_type=stats_type, id=message.author.id))
            await conn.execute("UPDATE users SET hug_count = {count} WHERE stats_type = '{stats_type}' AND discord_id = '{id}'".format(count=dates["hug_count"] + 1, stats_type=stats_type, id=who.id))
            em.description =  locale[lang]["fun_hug"].format(message.author.mention, who.mention)
            em.set_image(url=random.choice(hug_list))
    else:
        await conn.execute("INSERT INTO users(name, discord_id, stats_type) VALUES('{}', '{}', '{}')".format(clear_name(message.author.display_name[:50]), message.author.id, stats_type))
        em.description = locale[lang]["global_dont_have_that_much_money"].format(who=message.author.display_name+"#"+message.author.discriminator, money=const["server_money"])
        if not message.server.id in servers_without_follow_us:
            em = await add_follow_links(client, message, const, em)
    await client.send_message(message.channel, embed=em)
    return

async def f_kiss(client, conn, context, who):
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
    if not const or not const["is_kiss"]:
        em.description = locale[lang]["global_not_available"].format(who=message.author.display_name+"#"+message.author.discriminator)
        await client.send_message(message.channel, embed=em)
        return
    try:
        await client.delete_message(message)
    except:
        pass
    if await are_you_nitty(client, lang, who, message):
        return
    if not const["is_global"]:
        stats_type = message.server.id
    else:
        stats_type = "global"
    dat = await conn.fetchrow("SELECT cash FROM users WHERE stats_type = '{stats_type}' AND discord_id = '{id}'".format(stats_type=stats_type, id=message.author.id))
    dates = await conn.fetchrow("SELECT kiss_count FROM users WHERE stats_type = '{stats_type}' AND discord_id = '{id}'".format(stats_type=stats_type, id=who.id))
    if not dates:
        await conn.execute("INSERT INTO users(name, discord_id, stats_type) VALUES('{}', '{}', '{}')".format(clear_name(who.display_name[:50]), who.id, stats_type))
        dates = await conn.fetchrow("SELECT kiss_count FROM users WHERE stats_type = '{stats_type}' AND discord_id = '{id}'".format(stats_type=stats_type, id=who.id))
    if dat:
        if (const["kiss_price"] > dat["cash"]):
            em.description =  locale[lang]["global_dont_have_that_much_money"].format(who=message.author.display_name+"#"+message.author.discriminator, money=const["server_money"])
            if not message.server.id in servers_without_follow_us:
                em = await add_follow_links(client, message, const, em)
        else:
            await conn.execute("UPDATE users SET cash = {cash} WHERE stats_type = '{stats_type}' AND discord_id = '{id}'".format(stats_type=stats_type, cash=dat["cash"] - const["kiss_price"], id=message.author.id))
            await conn.execute("UPDATE users SET kiss_count = {count} WHERE stats_type = '{stats_type}' AND discord_id = '{id}'".format(stats_type=stats_type, count=dates["kiss_count"] + 1, id=who.id))
            em.description =  locale[lang]["fun_kiss"].format(message.author.mention, who.mention)
            em.set_image(url=random.choice(kiss_list))
    else:
        await conn.execute("INSERT INTO users(name, discord_id, stats_type) VALUES('{}', '{}', '{}')".format(clear_name(message.author.display_name[:50]), message.author.id, stats_type))
        em.description = locale[lang]["global_dont_have_that_much_money"].format(who=message.author.display_name+"#"+message.author.discriminator, money=const["server_money"])
        if not message.server.id in servers_without_follow_us:
            em = await add_follow_links(client, message, const, em)
    await client.send_message(message.channel, embed=em)
    return

async def f_five(client, conn, context, who):
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
    if not const or not const["is_five"]:
        em.description = locale[lang]["global_not_available"].format(who=message.author.display_name+"#"+message.author.discriminator)
        await client.send_message(message.channel, embed=em)
        return
    try:
        await client.delete_message(message)
    except:
        pass
    if await are_you_nitty(client, lang, who, message):
        return
    if not const["is_global"]:
        stats_type = message.server.id
    else:
        stats_type = "global"
    dat = await conn.fetchrow("SELECT cash, five_count FROM users WHERE stats_type = '{stats_type}' AND discord_id = '{id}'".format(stats_type=stats_type, id=message.author.id))
    if dat:
        if (const["five_price"] > dat["cash"]):
            em.description =  locale[lang]["global_dont_have_that_much_money"].format(who=message.author.display_name+"#"+message.author.discriminator, money=const["server_money"])
            if not message.server.id in servers_without_follow_us:
                em = await add_follow_links(client, message, const, em)
        else:
            await conn.execute("UPDATE users SET cash = {cash}, five_count = {count} WHERE stats_type = '{stats_type}' AND discord_id = '{id}'".format(
                stats_type=stats_type,
                cash=dat["cash"] - const["five_price"],
                count=dat["five_count"]+1,
                id=message.author.id
            ))
            em.description =  locale[lang]["fun_five"].format(message.author.mention, who.mention)
            em.set_image(url=random.choice(five_list))
    else:
        await conn.execute("INSERT INTO users(name, discord_id, stats_type) VALUES('{}', '{}', '{}')".format(clear_name(message.author.display_name[:50]), message.author.id, stats_type))
        em.description = locale[lang]["global_dont_have_that_much_money"].format(who=message.author.display_name+"#"+message.author.discriminator, money=const["server_money"])
        if not message.server.id in servers_without_follow_us:
            em = await add_follow_links(client, message, const, em)
    await client.send_message(message.channel, embed=em)
    return

async def f_punch(client, conn, context, who):
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
    if not const or not const["is_punch"]:
        em.description = locale[lang]["global_not_available"].format(who=message.author.display_name+"#"+message.author.discriminator)
        await client.send_message(message.channel, embed=em)
        return
    try:
        await client.delete_message(message)
    except:
        pass
    if await are_you_nitty(client, lang, who, message):
        return
    if not const["is_global"]:
        stats_type = message.server.id
    else:
        stats_type = "global"
    dat = await conn.fetchrow("SELECT cash FROM users WHERE stats_type = '{stats_type}' AND discord_id = '{id}'".format(stats_type=stats_type, id=message.author.id))
    dates = await conn.fetchrow("SELECT punch_count FROM users WHERE stats_type = '{stats_type}' AND discord_id = '{id}'".format(stats_type=stats_type, id=who.id))
    if not dates:
        await conn.execute("INSERT INTO users(name, discord_id, stats_type) VALUES('{}', '{}', '{}')".format(clear_name(who.display_name[:50]), who.id, stats_type))
        dates = await conn.fetchrow("SELECT punch_count FROM users WHERE stats_type = '{stats_type}' AND discord_id = '{id}'".format(stats_type=stats_type, id=who.id))
    if dat:
        if (const["punch_price"] > dat["cash"]):
            em.description =  locale[lang]["global_dont_have_that_much_money"].format(who=message.author.display_name+"#"+message.author.discriminator, money=const["server_money"])
            if not message.server.id in servers_without_follow_us:
                em = await add_follow_links(client, message, const, em)
        else:
            await conn.execute("UPDATE users SET cash = {cash} WHERE stats_type = '{stats_type}' AND discord_id = '{id}'".format(stats_type=stats_type, cash=dat["cash"] - const["punch_price"], id=message.author.id))
            await conn.execute("UPDATE users SET punch_count = {count} WHERE stats_type = '{stats_type}' AND discord_id = '{id}'".format(stats_type=stats_type, count=dates["punch_count"] + 1, id=who.id))
            em.description =  locale[lang]["fun_punch"].format(message.author.mention, who.mention)
            em.set_image(url=random.choice(punch_list))
    else:
        await conn.execute("INSERT INTO users(name, discord_id, stats_type) VALUES('{}', '{}', '{}')".format(clear_name(message.author.display_name[:50]), message.author.id, stats_type))
        em.description = locale[lang]["global_dont_have_that_much_money"].format(who=message.author.display_name+"#"+message.author.discriminator, money=const["server_money"])
        if not message.server.id in servers_without_follow_us:
            em = await add_follow_links(client, message, const, em)
    await client.send_message(message.channel, embed=em)
    return

async def f_fuck(client, conn, context, who):
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
    if not const or not const[3]:
        em.description = locale[lang]["global_not_available"].format(who=message.author.display_name+"#"+message.author.discriminator)
        await client.send_message(message.channel, embed=em)
        return
    try:
        await client.delete_message(message)
    except:
        pass
    if await are_you_nitty(client, lang, who, message):
        return
    if not const["is_global"]:
        stats_type = message.server.id
    else:
        stats_type = "global"
    dat = await conn.fetchrow("SELECT cash, fuck_count FROM users WHERE stats_type = '{stats_type}' AND discord_id = '{id}'".format(stats_type=stats_type, id=message.author.id))
    if dat:
        if (const["fuck_price"] > dat["cash"]):
            em.description =  locale[lang]["global_dont_have_that_much_money"].format(who=message.author.display_name+"#"+message.author.discriminator, money=const["server_money"])
            if not message.server.id in servers_without_follow_us:
                em = await add_follow_links(client, message, const, em)
        else:
            await conn.execute("UPDATE users SET cash = {cash}, fuck_count = {count} WHERE stats_type = '{stats_type}' AND discord_id = '{id}'".format(
                stats_type=stats_type,
                cash=dat["cash"] - const["fuck_price"],
                count=dat["fuck_count"]+1,
                id=message.author.id
            ))
            em.description =  locale[lang]["fun_fuck"].format(message.author.mention, who.mention)
            em.set_image(url=random.choice(fuck_list))
    else:
        await conn.execute("INSERT INTO users(name, discord_id, stats_type) VALUES('{}', '{}', '{}')".format(clear_name(message.author.display_name[:50]), message.author.id, stats_type))
        em.description = locale[lang]["global_dont_have_that_much_money"].format(who=message.author.display_name+"#"+message.author.discriminator, money=const["server_money"])
        if not message.server.id in servers_without_follow_us:
            em = await add_follow_links(client, message, const, em)
    await client.send_message(message.channel, embed=em)
    return

async def f_wink(client, conn, context, who):
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
    if not const or not const["is_wink"]:
        em.description = locale[lang]["global_not_available"].format(who=message.author.display_name+"#"+message.author.discriminator)
        await client.send_message(message.channel, embed=em)
        return
    try:
        await client.delete_message(message)
    except:
        pass
    if await are_you_nitty(client, lang, who, message):
        return
    if not const["is_global"]:
        stats_type = message.server.id
    else:
        stats_type = "global"
    dat = await conn.fetchrow("SELECT cash, wink_count FROM users WHERE stats_type = '{stats_type}' AND discord_id = '{id}'".format(stats_type=stats_type, id=message.author.id))
    if dat:
        if (const["wink_price"] > dat["cash"]):
            em.description =  locale[lang]["global_dont_have_that_much_money"].format(who=message.author.display_name+"#"+message.author.discriminator, money=const["server_money"])
            if not message.server.id in servers_without_follow_us:
                em = await add_follow_links(client, message, const, em)
        else:
            await conn.execute("UPDATE users SET cash = {cash}, wink_count = {count} WHERE stats_type = '{stats_type}' AND discord_id = '{id}'".format(
                stats_type=stats_type,
                cash=dat["cash"] - const["wink_price"],
                count=dat["wink_count"]+1,
                id=message.author.id
            ))
            em.description =  locale[lang]["fun_wink"].format(message.author.mention, who.mention)
            em.set_image(url=random.choice(wink_list))
    else:
        await conn.execute("INSERT INTO users(name, discord_id, stats_type) VALUES('{}', '{}', '{}')".format(clear_name(message.author.display_name[:50]), message.author.id, stats_type))
        em.description = locale[lang]["global_dont_have_that_much_money"].format(who=message.author.display_name+"#"+message.author.discriminator, money=const["server_money"])
        if not message.server.id in servers_without_follow_us:
            em = await add_follow_links(client, message, const, em)
    await client.send_message(message.channel, embed=em)
    return

async def f_drink(client, conn, context):
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
    if not const or not const["is_drink"]:
        em.description = locale[lang]["global_not_available"].format(who=message.author.display_name+"#"+message.author.discriminator)
        await client.send_message(message.channel, embed=em)
        return
    try:
        await client.delete_message(message)
    except:
        pass
    if not const["is_global"]:
        stats_type = message.server.id
    else:
        stats_type = "global"
    dat = await conn.fetchrow("SELECT cash, drink_count FROM users WHERE stats_type = '{stats_type}' AND discord_id = '{id}'".format(stats_type=stats_type, id=message.author.id))
    if dat:
        if (const["drink_price"] > dat["cash"]):
            em.description =  locale[lang]["global_dont_have_that_much_money"].format(who=message.author.display_name+"#"+message.author.discriminator, money=const["server_money"])
            if not message.server.id in servers_without_follow_us:
                em = await add_follow_links(client, message, const, em)
        else:
            await conn.execute("UPDATE users SET cash = {cash}, drink_count = {count} WHERE stats_type = '{stats_type}' AND discord_id = '{id}'".format(
                stats_type=stats_type,
                cash=dat["cash"] - const["drink_price"],
                count=dat["drink_count"]+1,
                id=message.author.id
            ))
            em.description =  locale[lang]["fun_drink"].format(message.author.mention)
            em.set_image(url=random.choice(drink_list))
    else:
        await conn.execute("INSERT INTO users(name, discord_id, stats_type) VALUES('{}', '{}', '{}')".format(clear_name(message.author.display_name[:50]), message.author.id, stats_type))
        em.description = locale[lang]["global_dont_have_that_much_money"].format(who=message.author.display_name+"#"+message.author.discriminator, money=const["server_money"])
        if not message.server.id in servers_without_follow_us:
            em = await add_follow_links(client, message, const, em)
    await client.send_message(message.channel, embed=em)
    return

async def f_rep(client, conn, context, who):
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
    if not const or not const["is_rep"]:
        em.description = locale[lang]["global_not_available"].format(who=message.author.display_name+"#"+message.author.discriminator)
        await client.send_message(message.channel, embed=em)
        return
    try:
        await client.delete_message(message)
    except:
        pass
    if await are_you_nitty(client, lang, who, message):
        return
    if not const["is_global"]:
        stats_type = message.server.id
    else:
        stats_type = "global"
    dat = await conn.fetchrow("SELECT rep_time FROM users WHERE stats_type = '{stats_type}' AND discord_id = '{id}'".format(stats_type=stats_type, id=message.author.id))
    dates = await conn.fetchrow("SELECT reputation FROM users WHERE stats_type = '{stats_type}' AND discord_id = '{id}'".format(stats_type=stats_type, id=who.id))
    if not dates:
        await conn.execute("INSERT INTO users(name, discord_id, stats_type) VALUES('{}', '{}', '{}')".format(clear_name(who.display_name[:50]), who.id, stats_type))
        dates = await conn.fetchrow("SELECT reputation FROM users WHERE stats_type = '{stats_type}' AND discord_id = '{id}'".format(stats_type=stats_type, id=who.id))
    if not dat:
        await conn.execute("INSERT INTO users(name, discord_id, stats_type) VALUES('{}', '{}', '{}')".format(clear_name(message.author.display_name[:50]), message.author.id, stats_type))
        dat = await conn.fetchrow("SELECT rep_time FROM users WHERE stats_type = '{stats_type}' AND discord_id = '{id}'".format(stats_type=stats_type, id=message.author.id))
    tim = int(time.time()) - dat["rep_time"]
    if tim < const["rep_cooldown"]:
        t=const["rep_cooldown"] - tim
        h=str(t//3600)
        m=str((t//60)%60)
        s=str(t%60)
        em.description = "{later1}\n{later2}".format(
        later1=locale[lang]["rep_try_again_later1"].format(
            who=clear_name(message.author.display_name+"#"+message.author.discriminator)
            ),
        later2=locale[lang]["rep_try_again_later2"].format(
            hours=h,
            minutes=m,
            seconds=s
            )
        )
        if not message.server.id in servers_without_follow_us:
            em = await add_follow_links(client, message, const, em)
    else:
        await conn.execute("UPDATE users SET rep_time = {time} WHERE stats_type = '{stats_type}' AND discord_id = '{id}'".format(
            time=int(time.time()),
            stats_type=stats_type,
            id=message.author.id
        ))
        await conn.execute("UPDATE users SET reputation = {rep} WHERE stats_type = '{stats_type}' AND discord_id = '{id}'".format(
            rep=dates["reputation"] + 3,
            stats_type=stats_type,
            id=who.id
        ))
        em.description =  locale[lang]["fun_rep_success"].format(message.author.mention, who.mention)
    await client.send_message(message.channel, embed=em)
    return

async def f_sex(client, conn, context, who):
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
    if not const or not const["is_sex"]:
        em.description = locale[lang]["global_not_available"].format(who=message.author.display_name+"#"+message.author.discriminator)
        await client.send_message(message.channel, embed=em)
        return
    try:
        await client.delete_message(message)
    except:
        pass
    if await are_you_nitty(client, lang, who, message):
        return
    if not const["is_global"]:
        stats_type = message.server.id
    else:
        stats_type = "global"
    dat = await conn.fetchrow("SELECT cash, sex_count FROM users WHERE stats_type = '{stats_type}' AND discord_id = '{id}'".format(stats_type=stats_type, id=message.author.id))
    dates = await conn.fetchrow("SELECT sex_count FROM users WHERE stats_type = '{stats_type}' AND discord_id = '{id}'".format(stats_type=stats_type, id=who.id))
    if not dates:
        await conn.execute("INSERT INTO users(name, discord_id, stats_type) VALUES('{}', '{}', '{}')".format(clear_name(who.display_name[:50]), who.id, stats_type))
        dates = await conn.fetchrow("SELECT sex_count FROM users WHERE stats_type = '{stats_type}' AND discord_id = '{id}'".format(stats_type=stats_type, id=who.id))
    if dat:
        if (const["sex_price"] > dat["cash"]):
            em.description = locale[lang]["global_dont_have_that_much_money"].format(who=message.author.display_name+"#"+message.author.discriminator, money=const["server_money"])
            if not message.server.id in servers_without_follow_us:
                em = await add_follow_links(client, message, const, em)
        else:
            await conn.execute("UPDATE users SET cash = {cash} WHERE stats_type = '{stats_type}' AND discord_id = '{id}'".format(
                cash=dat["cash"] - const["sex_price"],
                stats_type=stats_type,
                id=message.author.id
            ))
            await conn.execute("UPDATE users SET sex_count = {count} WHERE stats_type = '{stats_type}' AND discord_id = '{id}'".format(
                count=dates["sex_count"] + 1,
                stats_type=stats_type,
                id=who.id
            ))
            em.description =  "{} трахнул(а) {}".format(message.author.mention, who.mention)
            em.set_image(url=random.choice(sex_list))
    else:
        await conn.execute("INSERT INTO users(name, discord_id, stats_type) VALUES('{}', '{}', '{}')".format(clear_name(message.author.display_name[:50]), message.author.id, stats_type))
        em.description = locale[lang]["global_dont_have_that_much_money"].format(who=message.author.display_name+"#"+message.author.discriminator, money=const["server_money"])
        if not message.server.id in servers_without_follow_us:
            em = await add_follow_links(client, message, const, em)
    await client.send_message(message.channel, embed=em)
    return

async def are_you_nitty(client, lang, who, message):
    em = discord.Embed(colour=0xC5934B)
    if not who:
        em.description = locale[lang]["global_not_mention_on_user"].format(message.author.display_name+"#"+message.author.discriminator)
    elif who.bot:
        em.description = locale[lang]["global_bot_mentioned"].format(
            who=message.author.display_name+"#"+message.author.discriminator,
            bot=who.display_name[:50]
        )
    elif message.author == who:
        em.description = locale[lang]["global_choose_someone_else"].format(message.author.display_name+"#"+message.author.discriminator)
    else:
        return False
    await client.send_message(message.channel, embed=em)
    return True


async def f_top(client, conn, context, page, type):
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
    if not const or not const["is_me"]:
        em.description = locale[lang]["global_not_available"].format(who=message.author.display_name+"#"+message.author.discriminator)
        await client.send_message(message.channel, embed=em)
        return
    try:
        await client.delete_message(message)
    except:
        pass
    await client.send_typing(message.channel)
    if not const["is_global"]:
        stats_type = message.server.id
    else:
        stats_type = "global"
    dat = await conn.fetchrow("SELECT COUNT(name) FROM users WHERE stats_type = '{}'".format(stats_type))
    all_count = dat[0]
    pages = (((all_count - 1) // 5) + 1)
    if not page:
        page = 1
    if all_count == 0:
        em.description = locale[lang]["global_list_is_empty"]
        await client.send_message(message.channel, embed=em)
        return
    if page > pages:
        em.description = locale[lang]["global_page_not_exists"].format(who=message.author.display_name+"#"+message.author.discriminator, number=page)
        await client.send_message(message.channel, embed=em)
        return
    if type == "xp":
        order = "xp_count"
    elif type == "money":
        order = "cash"
    elif type == "voice":
        order = "voice_time"
    else:
        order = "name"
    dat = await conn.fetch("SELECT * FROM users WHERE stats_type = '{stats_type}' ORDER BY {order} DESC LIMIT 5 OFFSET {offset}".format(order=order, stats_type=stats_type, offset=(page-1)*5))
#==================================================
    img = Image.open("cogs/stat/top5.png")
    back = Image.open("cogs/stat/top5.png")
    draw = ImageDraw.Draw(img)
    draws = ImageDraw.Draw(back)

    font_position = ImageFont.truetype("cogs/stat/Roboto-Bold.ttf", 24)
    font_count = ImageFont.truetype("cogs/stat/Roboto-Regular.ttf", 16)

    for i, user in enumerate(dat):
        name = user["name"]
        name = u"{}".format(name)
        name_size = 1
        font_name = ImageFont.truetype("cogs/stat/Roboto-Bold.ttf", name_size)
        while font_name.getsize(name)[0] < 180:
            name_size += 1
            font_name = ImageFont.truetype("cogs/stat/Roboto-Bold.ttf", name_size)
            if name_size == 31:
                break
        name_size -= 1
        font_name = ImageFont.truetype("cogs/stat/Roboto-Bold.ttf", name_size)
        if not name:
            name = " "
        ava_url = user["avatar_url"]
        if ava_url:
            try:
                response = str(requests.session().get(ava_url).content)
                if not response[2:-1]:
                    ava_url = None
            except:
                ava_url = None
        if not ava_url:
            ava_url = client.user.default_avatar_url
            for server in client.servers:
                member = server.get_member(user["discord_id"])
                if member and member.avatar_url:
                    ava_url = member.avatar_url
                    await conn.execute("UPDATE users SET avatar_url = '{url}' WHERE stats_type = '{stats_type}' AND discord_id = '{id}'".format(
                        url=ava_url,
                        stats_type=stats_type,
                        id=user["discord_id"]
                    ))
                    break
        response = requests.get(ava_url)
        avatar = Image.open(BytesIO(response.content)).convert('RGB')
        avatar_circle = avatar.resize((549, 549))
        avatar_circle.putalpha(mask_top_back)
        avatar_circle = avatar_circle.crop((274, 0, 474, 549))
        back.paste(avatar_circle, (i*200, 0), avatar_circle)
        avatar_circle = avatar.resize((269, 269))
        bigsize = (avatar_circle.size[0] * 3, avatar_circle.size[1] * 3)
        avatar_circle.putalpha(mask_top)
        avatar_circle = avatar_circle.crop((0, 0, 134, 269))
        img.paste(avatar_circle, (66+i*200, 125), avatar_circle)
        position = "#{}".format(i+1+(page-1)*5)
        draw.text(
            (
                100-font_position.getsize(position)[0]/2+i*200,
                440-font_position.getsize(position)[1]/2
            ),
            position,
            (255, 255, 255),
            font=font_position
        )
        draw.text((100-font_name.getsize(name)[0]/2+i*200, 50-font_name.getsize(name)[1]/2), name, (255, 255, 255), font=font_name)
        if type == "xp":
            count = locale[lang]["fun_top5_xp_count"].format((user["xp_count"]))
            _type = "xp"
        elif type == "money":
            count = "{}$".format((user["cash"]))
            _type = "money"
        elif type == "voice":
            hours=str(user["voice_time"]//3600)
            minutes=str((user["voice_time"]//60)%60)
            seconds=str(user["voice_time"]%60)
            count = "{h}h {m}m {s}s".format(
                h=hours,
                m=minutes,
                s=seconds
            )
            _type = "voice"
        else:
            count = "0"
            _type = "name"
        draw.text(
            (
                100-font_count.getsize(count)[0]/2+i*200,
                475-font_count.getsize(count)[1]/2
            ),
            count,
            (255, 255, 255),
            font=font_count
        )

    back.paste(img, (0, 0), img)

    back.save('cogs/stat/return/top/{}.png'.format(message.author.id))
    await client.send_file(message.channel, "cogs/stat/return/top/{}.png".format(message.author.id), content=locale[lang]["fun_top5_response"].format(
        type=locale[lang]["fun_top5_type_"+_type]
    ))
    os.remove("cogs/stat/return/top/{}.png".format(message.author.id))
    return
