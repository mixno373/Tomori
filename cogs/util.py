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
import imghdr
import os
import re
from PIL import Image, ImageChops, ImageFont, ImageDraw, ImageSequence, ImageFilter
from PIL.GifImagePlugin import getheader, getdata
from functools import partial
import aiohttp
from aiohttp import ClientSession
from io import BytesIO
from typing import Union
from discord.ext import commands
from config.settings import settings
from cogs.locale import *
from cogs.const import *
from cogs.ids import *
from cogs.discord_hooks import Webhook
from config.constants import *



mask = Image.new('L', (1002, 1002), 0)
draws = ImageDraw.Draw(mask)
draws.ellipse((471, 5) + (531, 35), fill=255)
draws.ellipse((471, 967) + (531, 997), fill=255)
draws.ellipse((5, 471) + (35, 531), fill=255)
draws.ellipse((967, 471) + (997, 531), fill=255)
draws.polygon([(531, 15), (471, 15), (15, 471), (15, 531), (471, 987), (531, 987), (987, 531), (987, 471)], fill=255)
mask = mask.resize((343, 343), Image.ANTIALIAS)



async def is_it_has_badge(conn, client, notify, message, badge):
    if not badge.lower() in await check_badges(conn, message.author.id, badge.lower()):
        em = discord.Embed(
            colour=0xC5934B,
            description=locale["english"]["global_have_not_badge"].format(who=tagged_dname(message.author), badge=badge)
        )
        if notify:
            try:
                await asyncio.wait([
                    client.delete_message(message),
                    client.send_message(message.channel, embed=em)
                ])
            except:
                pass
        return False
    return True




async def u_setvoice(client, conn, logger, context):
    message = context.message
    server_id = message.server.id
    who = message.author
    const = await get_cached_server(conn, server_id)
    lang = const[2]
    if not const or not const[1]:
        await send_command_error(message, lang)
        return
    em = discord.Embed(colour=int(const[0], 16) + int("0x200", 16))
    try:
        await client.delete_message(message)
    except:
        pass
    if not who.voice.voice_channel:
        logger.error('Сервер {0.name} | {0.id}. Пользователь не в войсе. User - {1.name} | {1.id}\n'.format(who.server, who))
        em.description = '{}, для начала зайдите в голосовой канал.'.format(clear_name(who.display_name[:50]))
        await client.send_message(message.channel, embed=em)
        return
    try:
        await conn.execute("UPDATE settings SET create_lobby_id = '{}' WHERE discord_id = '{}'".format(who.voice.voice_channel.id, server_id))
        pop_cached_server(server_id)
        logger.error('Сервер {0.name} | {0.id}. Установлен войс канал. User - {1.name} | {1.id}\n'.format(who.server, who))
        em.description = '{}, войс для лобби установлен.'.format(clear_name(who.display_name[:50]))
        await client.send_message(message.channel, embed=em)
        return
    except:
        logger.error('Сервер {0.name} | {0.id}. Не удалось установить канал. User - {1.name} | {1.id}\n'.format(who.server, who))
        em.description = '{}, не удалось установить канал.'.format(clear_name(who.display_name[:50]))
        await client.send_message(message.channel, embed=em)
        return

async def u_setlobby(client, conn, logger, context):
    message = context.message
    server_id = message.server.id
    who = message.author
    const = await conn.fetchrow("SELECT em_color, is_createvoice, locale FROM settings WHERE discord_id = '{}'".format(server_id))
    lang = const[2]
    if not const or not const[1]:
        await send_command_error(message, lang)
        return
    em = discord.Embed(colour=int(const[0], 16) + int("0x200", 16))
    try:
        await client.delete_message(message)
    except:
        pass
    if not who.voice.voice_channel:
        logger.error('Сервер {0.name} | {0.id}. Пользователь не в войсе. User - {1.name} | {1.id}\n'.format(who.server, who))
        em.description = '{}, для начала зайдите в голосовой канал.'.format(clear_name(who.display_name[:50]))
        await client.send_message(message.channel, embed=em)
        return
    try:
        await client.edit_channel_permissions(who.voice.voice_channel, target=who.server.default_role, overwrite=discord.PermissionOverwrite(read_messages=True, move_members=True))
        logger.error('Сервер {0.name} | {0.id}. Установлен войс лобби. User - {1.name} | {1.id}\n'.format(who.server, who))
        em.description = '{}, войс для ожидания лобби установлен.'.format(clear_name(who.display_name[:50]))
        await client.send_message(message.channel, embed=em)
        return
    except:
        logger.error('Сервер {0.name} | {0.id}. Не удалось установить канал. User - {1.name} | {1.id}\n'.format(who.server, who))
        em.description = '{}, не удалось установить канал.'.format(clear_name(who.display_name[:50]))
        await client.send_message(message.channel, embed=em)
        return

async def u_news(client, conn, context, message_id):
    server_count = 0
    message = context.message
    channel_from = message.channel
    em = discord.Embed(colour=0xC5934B)
    try:
        await client.delete_message(message)
    except:
        pass
    try:
        message_from = await client.get_message(channel_from, message_id)
        content = message_from.content
        if not content:
            em.description = "Некорректное сообщение."
            em.set_footer(text="Время ответа - {}ms".format(int((datetime.utcnow() - message.timestamp).microseconds / 1000)))
            await client.send_message(channel_from, embed=em)
            return
        servers_ids = await conn.fetch("SELECT discord_id FROM settings WHERE is_news = True")
        if servers_ids:
            for server_id in servers_ids:
                server = client.get_server(server_id)
                for channel in server.channels:
                    if channel.name.lower() == "tomori news":
                        await client.send_message(channel, content)
                        server_count += 1
                        break
                else:
                    channel = await client.create_channel(server, "Tomori News")
                    await client.send_message(channel, content)
                    server_count += 1
    except:
        em.description = "Некорректный id."
        em.set_footer(text="Время ответа - {}ms".format(int((datetime.utcnow() - message.timestamp).microseconds / 1000)))
        await client.send_message(channel_from, embed=em)
    em.description = "Успешно отправлено на {} серверов!".format(server_count)
    em.set_footer(text="Время ответа - {}ms".format(int((datetime.utcnow() - message.timestamp).microseconds / 1000)))
    await client.send_message(channel_from, embed=em)
    await client.send_message(channel_from, "Успешно отправлено на {} серверов!".format(server_count))

async def u_reaction_add(client, conn, logger, data):
    emoji = data.get("emoji")
    user_id = data.get("user_id")
    message_id = data.get("message_id")
    server_id = data.get("guild_id")
    server = client.get_server(server_id)
    user = server.get_member(user_id)
    if server_id in not_log_servers:
        return
    data = await conn.fetch("SELECT * FROM mods WHERE server_id = '{server_id}' AND type = 'reaction' AND name = '{name}'".format(
        server_id=server.id,
        name=message_id
    ))
    roles = []
    for role in user.roles:
        if not any(role.id==dat["value"] for dat in data) or any(dat["value"]=='not unique' for dat in data):
            roles.append(role)
    is_new_role = False
    if any(dat["value"]=='random' for dat in data):
        random_roles = []
        for react in data:
            if not react["condition"] == emoji['name']:
                continue
            role = discord.utils.get(server.roles, id=react["value"])
            if role and not (role in roles or role in random_roles):
                is_new_role = True
                random_roles.append(role)
        roles.append(random.choice(random_roles))
    else:
        for react in data:
            if not react["condition"] == emoji['name']:
                continue
            role = discord.utils.get(server.roles, id=react["value"])
            if role and not role in roles:
                is_new_role = True
                roles.append(role)
    if is_new_role:
        try:
            await client.replace_roles(user, *roles)
        except:
            pass

async def u_reaction_remove(client, conn, logger, data):
    emoji = data.get("emoji")
    user_id = data.get("user_id")
    message_id = data.get("message_id")
    server_id = data.get("guild_id")
    server = client.get_server(server_id)
    user = server.get_member(user_id)
    if server_id in not_log_servers:
        return
    data = await conn.fetch("SELECT * FROM mods WHERE server_id = '{server_id}' AND type = 'reaction' AND name = '{name}'".format(
        server_id=server.id,
        name=message_id,
        condition=emoji["name"]
    ))
    roles = []
    for react in data:
        if not react["condition"] == emoji['name']:
            continue
        role = discord.utils.get(server.roles, id=react["value"])
        if not role:
            logger.error("doesn't exists role id - {id}".format(id=react["value"]))
        else:
            roles.append(role)
    if roles:
        await client.remove_roles(user, *roles)



async def u_check_travelling(client, member):
    global travelling_servers
    if not travelling_servers:
        return
    server_id = travelling_servers.get(member.server.id)
    if not server_id:
        return
    server = client.get_server(server_id)
    if not server:
        return
    user = server.get_member(member.id)
    if not user:
        return
    roles = user.roles
    _roles = member.server.roles
    added_roles = []
    for role in roles:
        _role = discord.utils.get(
            _roles,
            name=role.name,
            permissions=role.permissions,
            colour=role.colour,
            hoist=role.hoist,
            mentionable=role.mentionable
        )
        if _role:
            added_roles.append(_role)
    if added_roles:
        await client.add_roles(member, *added_roles)
    #await client.kick(user)



async def u_response_moon_server(client, const, message, comm_name):
    global moon_server
    who = None
    arg1 = message.content.split(" ", maxsplit=1)
    if len(arg1) > 1:
        arg1 = arg1[1]
    else:
        arg1 = None
    if arg1:
        who = discord.utils.get(message.server.members, name=arg1)
        if not who:
            arg1 = re.sub(r'[<@#&!>]+', '', arg1)
            who = discord.utils.get(message.server.members, id=arg1)
    if moon_server.get(comm_name).get("is_who", "") == "True" and not who:
        await client.send_message(message.channel, "{who}, Ты не выбрал пользователя для этого действия(".format(who=message.author.mention))
        return
    em = discord.Embed(colour=int(const["em_color"], 16) + 512)
    if moon_server.get(comm_name).get("is_who", "") == "True":
        text = moon_server.get(comm_name).get("response").format(author=message.author.mention, user=who.mention)
    else:
        text = moon_server.get(comm_name).get("response").format(author=message.author.mention)
    em.description = text
    em.set_image(url=random.choice(moon_server.get(comm_name).get("gifs")))
    await client.send_message(message.channel, embed=em)




async def u_invite_to_server(client, server_id):
    server = client.get_server(server_id)
    if not server:
        return None
    try:
        invites = await client.invites_from(server)
        for invite in invites:
            if invite.max_age == 0 and invite.max_uses == 0:
                return invite.url
        return invites[0].url
    except:
        pass
    try:
        invite = await client.create_invite(server, max_age=0, max_uses=0)
        return invite.url
    except:
        pass
    for channel in server.channels:
        try:
            invite = await client.create_invite(channel, max_age=0, max_uses=0)
            if not invite.url:
                continue
            return invite.url
        except:
            pass
    return None

async def u_check_invite(client, url):
    try:
        invite = await client.get_invite(url)
        return True
    except:
        return False

async def u_invite_server(client, conn, context, server_id):
    message = context.message
    try:
        await client.delete_message(message)
    except:
        pass
    em = discord.Embed(colour=0xC5934B)
    server = client.get_server(server_id)
    if not server:
        em.description = "Сервер (ID:{id}) - не существует.".format(id=server_id)
        await client.send_message(message.channel, embed=em)
        return
    try:
        invites = await client.invites_from(server)
        for invite in invites:
            if invite.max_age == 0 and invite.max_uses == 0:
                em.description = "Сервер (ID:{id}) one of invites:\n{invite}".format(id=server_id, invite=invite.url)
                await client.send_message(message.channel, embed=em)
                return
        em.description = "Сервер (ID:{id}) first of invites:\n{invite}".format(id=server_id, invite=invites[0].url)
        await client.send_message(message.channel, embed=em)
        return
    except:
        pass
    try:
        invite = await client.create_invite(server, max_age=0, max_uses=1)
        em.description = "Сервер (ID:{id}) invite created:\n{invite}".format(id=server_id, invite=invite.url)
        await client.send_message(message.channel, embed=em)
        return
    except:
        pass
    for channel in server.channels:
        try:
            invite = await client.create_invite(channel, max_age=0, max_uses=1)
            if not invite.url:
                continue
            em.description = "Сервер (ID:{id}) invite to channel {channel_name}:\n{invite}".format(id=server_id, invite=invite.url, channel_name=channel.name)
            await client.send_message(message.channel, embed=em)
            return
        except:
            pass
    else:
        em.description = "Сервер (ID:{id}) - не удалось создать инвайт ни в один канал.".format(id=server_id)
        await client.send_message(message.channel, embed=em)
        return

async def u_invite_channel(client, conn, context, channel_id):
    message = context.message
    try:
        await client.delete_message(message)
    except:
        pass
    em = discord.Embed(colour=0xC5934B)
    channel = client.get_channel(channel_id)
    if not channel:
        em.description = "Channel (ID:{id}) - не существует.".format(id=channel_id)
        await client.send_message(message.channel, embed=em)
        return
    try:
        invite = await client.create_invite(channel, max_age=0, max_uses=0)
        em.description = "Channel (ID:{id}) invite to channel {channel_name}:\n{invite}".format(id=channel_id, invite=invite.url, channel_name=channel.name)
        await client.send_message(message.channel, embed=em)
        return
    except:
        em.description = "Channel (ID:{id}) - не удалось создать инвайт в канал.".format(id=channel_id)
        await client.send_message(message.channel, embed=em)
        return

def u_get_channel(client, channel_id):
    channel = client.get_channel(channel_id)
    if not channel:
        for server in client.servers:
            channel = server.get_member(channel_id)
            if channel:
                break
    return channel

async def u_check_support(client, conn, logger, message):
    channel = message.channel
    if channel.is_private:
        chan_id = channel.user.id
    else:
        chan_id = channel.id

    if not channel.is_private:
        travel_to = travelling_message_servers.get(message.server.id)
        if travel_to and message.author.id != client.user.id and not message.author.bot:
            travel_server_to = client.get_server(travel_to)
            if travel_server_to:
                travel_channel_to = discord.utils.get(
                    travel_server_to.channels,
                    name=channel.name,
                    type=channel.type
                    # topic=channel.topic
                )
                if travel_channel_to:
                    em = discord.Embed(colour=0xC5934B)
                    em.description = message.content
                    icon_url = message.author.avatar_url
                    if not icon_url:
                        icon_url = message.author.default_avatar_url
                    em.set_author(name=message.author.name + "#" + message.author.discriminator, icon_url=icon_url)
                    em.set_footer(text="Отправлено с сервера "+message.server.name)
                    await client.send_message(travel_channel_to, embed=em)

    dat = await conn.fetchrow("SELECT * FROM tickets WHERE request_id = '{request_id}' OR response_id = '{response_id}'".format(request_id=chan_id, response_id=chan_id))
    if not dat:
        if channel.is_private and message.content:
            content = message.content
            dialogflow = apiai.ApiAI(settings["dialogflow_token"]).text_request()
            dialogflow.lang = 'ru'
            dialogflow.session_id = 'BatlabAIBot'
            dialogflow.query = content # Посылаем запрос к ИИ с сообщением от юзера
            responseJson = json.loads(dialogflow.getresponse().read().decode('utf-8'))
            response = responseJson['result']['fulfillment']['speech'] # Разбираем JSON и вытаскиваем ответ
            # Если есть ответ от бота - присылаем юзеру, если нет - бот его не понял
            try:
                if response:
                    # if message.server.id == '475425777215864833':
                    #     response = "<@!480694830721269761> " + response
                    await client.send_message(message.author, response)
                else:
                    await client.send_message(message.author, locale[lang]["support_idu"].format(mention=message.author.mention))
            except:
                pass
        return

    request_channel = u_get_channel(client, dat["request_id"])
    response_channel_id = dat["response_id"]
    if not message.author.bot and request_channel and not message.content == "!stop":
        em = discord.Embed(colour=0xC5934B)
        em.description = message.content
        if not channel.is_private:
            if channel.id == response_channel_id:
                index = 0
                name = None
                for s in support_list:
                    index += 1
                    if s == message.author.id:
                        name = "Tomori Support ✔"
                        icon_url = client.user.avatar_url
                        break
                if dat["name"]:
                    name = "{name}#{tag}".format(name=dat["name"], tag=message.author.discriminator)
                    icon_url = message.server.icon_url
                    if not icon_url:
                        icon_url = message.author.default_avatar_url
                if not name:
                    name = "{name}#{tag}".format(name=message.author.name, tag=message.author.discriminator)
                    icon_url = message.author.avatar_url
                    if not icon_url:
                        icon_url = message.author.default_avatar_url
                em.set_author(name=name, icon_url=icon_url)
                if message.content:
                    await client.send_message(request_channel, embed=em)
                for attachment in message.attachments:
                    em = discord.Embed(colour=0xC5934B)
                    em.set_author(name=name, icon_url=icon_url)
                    em.set_image(url=attachment["proxy_url"])
                    try:
                        await client.send_message(request_channel, embed=em)
                    except:
                        pass
            elif channel.id == request_channel.id:
                em.set_author(name=message.author.name + "#" + message.author.discriminator, icon_url=message.author.avatar_url)
                em.set_footer(text="ID: {id} • Mention: {mention}".format(
                    id=message.author.id,
                    mention=message.author.mention
                ))
                if message.content:
                    await client.send_message(u_get_channel(client, response_channel_id), embed=em)
                for attachment in message.attachments:
                    em = discord.Embed(colour=0xC5934B)
                    em.set_author(name=message.author.name + "#" + message.author.discriminator, icon_url=message.author.avatar_url)
                    em.set_image(url=attachment["proxy_url"])
                    try:
                        await client.send_message(u_get_channel(client, response_channel_id), embed=em)
                    except:
                        pass
        else:
            if channel.user.id == request_channel.id:
                em.set_author(name=message.author.name + "#" + message.author.discriminator, icon_url=message.author.avatar_url)
                em.set_footer(text="ID: {id} • Mention: {mention}".format(
                    id=message.author.id,
                    mention=message.author.mention
                ))
                if message.content:
                    await client.send_message(u_get_channel(client, response_channel_id), embed=em)
                for attachment in message.attachments:
                    em = discord.Embed(colour=0xC5934B)
                    em.set_author(name=message.author.name + "#" + message.author.discriminator, icon_url=message.author.avatar_url)
                    em.set_image(url=attachment["proxy_url"])
                    try:
                        await client.send_message(u_get_channel(client, response_channel_id), embed=em)
                    except:
                        pass
            elif channel.user.id == response_channel_id:
                index = 0
                name = None
                for s in support_list:
                    index += 1
                    if s == message.author.id:
                        name = "Tomori ✔"
                        icon_url = client.user.avatar_url
                        if not icon_url:
                            icon_url = message.author.default_avatar_url
                        break
                if dat["name"]:
                    name = "{name}#{tag}".format(name=dat["name"], tag=message.author.discriminator)
                    icon_url = message.author.avatar_url
                    if not icon_url:
                        icon_url = message.author.default_avatar_url
                if not name:
                    name = "{name}#{tag}".format(name=message.author.name, tag=message.author.discriminator)
                    icon_url = message.author.avatar_url
                    if not icon_url:
                        icon_url = message.author.default_avatar_url
                em.set_author(name=name, icon_url=icon_url)
                if message.content:
                    await client.send_message(request_channel, embed=em)
                for attachment in message.attachments:
                    em = discord.Embed(colour=0xC5934B)
                    em.set_author(name=name, icon_url=icon_url)
                    em.set_image(url=attachment["proxy_url"])
                    try:
                        await client.send_message(request_channel, embed=em)
                    except:
                        pass




async def check_captcha(client, conn, const, channel, member):
    captcha = random.choice(list(captcha_list.keys()))
    lang = const["locale"]
    em = discord.Embed(colour=int(const["em_color"], 16) + 512)
    em.description = locale[lang]["captcha_solve"].format(
        who=member.display_name+"#"+member.discriminator,
        text=captcha
    )
    await client.send_message(channel, embed=em)
    msg = await client.wait_for_message(timeout=60, author=member)
    if not msg or not msg.content or not msg.content.lower() == captcha_list.get(captcha):
        em.description = locale[lang]["captcha_wrong_solution"].format(who=member.display_name+"#"+member.discriminator)
        await client.send_message(channel, embed=em)
        return False
    else:
        return True

mask_captcha = Image.new('L', (1000, 1000), 0)
draws = ImageDraw.Draw(mask_captcha)
draws.rectangle((0, 350) + (1000, 650), fill=77)
mask_captcha = mask_captcha.resize((1000, 1000), Image.ANTIALIAS)

font_captcha_1 = ImageFont.truetype("cogs/stat/ProximaNova-Bold.otf", 100)
font_captcha_2 = ImageFont.truetype("cogs/stat/ProximaNova-Bold.otf", 200)

async def check_captcha_new(client, conn, const, channel, member):
    captcha = ""
    shift = random.randint(0, 1)
    for i in [1,0,1,0,1,0]:
        captcha += random.choice(captcha_symbols[(i+shift)%2])
    lang = const["locale"]
    content = locale[lang]["captcha_solve"].format(who=member.mention)

    ava_url = member.avatar_url
    if ava_url:
        try:
            response = str(requests.session().get(ava_url).content)
            if not response[2:-1]:
                ava_url = None
        except:
            ava_url = None
    if not ava_url:
        ava_url = member.default_avatar_url
    response = requests.get(ava_url)
    back = Image.open(BytesIO(response.content))
    back = back.resize((1000, 1000))
    back = back.filter(ImageFilter.GaussianBlur(15))
    back.putalpha(mask_captcha)
    back.crop((0, 350) + (1000, 650))
    draw = ImageDraw.Draw(back)

    draw.text(
        (back.size[0]-font_captcha_1.getsize(captcha)[0]/2, back.size[1]-font_captcha_1.getsize(captcha)[1]/2),
        captcha,
        (255, 255, 255),
        font=font_captcha_1
    )

    back.save('cogs/stat/return/captcha/{}.png'.format(member.id))
    await client.send_file(channel, "cogs/stat/return/captcha/{}.png".format(member.id), content=content)
    os.remove("cogs/stat/return/captcha/{}.png".format(member.id))

    msg = await client.wait_for_message(timeout=60, author=member)
    if not msg or not msg.content or not msg.content.lower() == captcha.lower():
        content = locale[lang]["captcha_wrong_solution"].format(who=member.mention)
        await client.send_message(channel, content)
        return False
    else:
        return True


def xp_to_lvl(xp, dirr="up"):
    if dirr == "up":
        for xp_count in sorted(xp_lvlup_list.keys(), key=lambda k: int(k), reverse=False):
            if xp < int(xp_count):
                return xp_lvlup_list[xp_count]
    if dirr == "down":
        for xp_count in sorted(xp_lvlup_list.keys(), key=lambda k: int(k), reverse=False):
            if xp < int(xp_count):
                return xp_lvlup_list[xp_count] - 1
    return None

async def u_check_voice_time(client, conn, const, user, voice_time, new_voice_time):
    if not const["is_global"]:
        stats_type = user.server.id
    else:
        stats_type = "global"
    n_v = int(new_voice_time / const["voice_seconds_to_award"])
    l_v = int((new_voice_time - voice_time) / const["voice_seconds_to_award"])
    diff = n_v - l_v
    if diff > 0:
        money = diff * const["voice_award_money"]
        xp = diff * const["voice_award_xp"]
        dat = await conn.fetchrow("UPDATE users SET cash = cash + {money}, xp_count = xp_count + {xp} WHERE discord_id = '{id}' AND stats_type = '{stats_type}' RETURNING *".format(
            money=money,
            xp=xp,
            id=user.id,
            stats_type=stats_type
        ))

        xp_last = int(dat["xp_count"]) - int(xp)
        xp_new = int(dat["xp_count"])
        lvl_last = None
        lvl_new = None

        lvl_last = xp_to_lvl(xp_last, "up")
        lvl_new = xp_to_lvl(xp_new, "down")
        if lvl_last and lvl_last == lvl_new:
            lang = const["locale"]
            if not lang in locale.keys():
                return

            em = discord.Embed(colour=int(const["em_color"], 16) + 512)
            em.set_author(name=user.server.name, icon_url=user.server.icon_url)
            em.description = locale[lang]["lvlup"].format(
                who=user.mention,
                lvl=lvl_last

            )
            data = await conn.fetch("SELECT * FROM mods WHERE server_id = '{server_id}' AND type = 'lvlup'".format(
                server_id=user.server.id
            ))
            roles = []
            is_new_role = False
            roles_mention = ""
            for role in user.roles:
                if not any(role.id==dat["value"] for dat in data):
                    roles.append(role)
            for dat in data:
                if not dat["condition"] == str(lvl_last):
                    continue
                role = discord.utils.get(user.server.roles, id=dat["value"])
                if role and not role in roles:
                    is_new_role = True
                    roles_mention += role.name+", "
                    roles.append(role)
            if is_new_role:
                em.description += locale[lang]["lvlup_continue"].format(role=roles_mention[:-2])
                try:
                    await client.replace_roles(user, *roles)
                except:
                    pass
            if not user.server.id in konoha_servers:
                em.set_image(url=lvlup_image_url)
            else:
                em.set_image(url=lvlup_image_konoha_url)
            try:
                msg = await client.send_message(user, embed=em)

            except:
                pass


async def u_check_lvlup(client, conn, channel, who, const, xp):
    lang = const["locale"]
    if not lang in locale.keys():
        return
    lvl = xp_lvlup_list.get(xp, 0)
    em = discord.Embed(colour=int(const["em_color"], 16) + 512)
    em.description = locale[lang]["lvlup"].format(
        who=who.mention,
        lvl=lvl
    )
    data = await conn.fetch("SELECT * FROM mods WHERE server_id = '{server_id}' AND type = 'lvlup'".format(
        server_id=who.server.id
    ))
    roles = []
    is_new_role = False
    roles_mention = ""
    for role in who.roles:
        if not any(role.id==dat["value"] for dat in data):
            roles.append(role)
    for dat in data:
        if not dat["condition"] == str(lvl):
            continue
        role = discord.utils.get(who.server.roles, id=dat["value"])
        if role and not role in roles:
            is_new_role = True
            roles_mention += role.mention+", "
            roles.append(role)
    if is_new_role:
        em.description += locale[lang]["lvlup_continue"].format(role=roles_mention[:-2])
        try:
            await client.replace_roles(who, *roles)
        except:
            pass
    if not who.server.id in konoha_servers:
        em.set_image(url=lvlup_image_url)
    else:
        em.set_image(url=lvlup_image_konoha_url)
    try:
        msg = await client.send_message(channel, embed=em)
        await asyncio.sleep(25)
        await client.delete_message(msg)
    except:
        pass


def welcomer_format(text, member):
    server = member.server
    return text.format(
        name=member.name,
        mention=member.mention,
        server=server.name,
        count=server.member_count
    )[:2000]

async def send_welcome_pic(client, channel, user, const):
    await client.send_typing(channel)

    color = json.loads(const["welcome_text_color"])

    back = Image.open("cogs/stat/backgrounds/welcome/{}.png".format(const["welcome_back"]))
    draw = ImageDraw.Draw(back)
    under = Image.open("cogs/stat/backgrounds/welcome/under_{}.png".format(const["welcome_under"]))

    text_welcome = ImageFont.truetype("cogs/stat/ProximaNova-Bold.otf", 50)
    text_name = ImageFont.truetype("cogs/stat/ProximaNova-Bold.otf", 50)

    text_welcome = u"{}".format("WELCOME")
    welcome_size = 1
    font_name = ImageFont.truetype("cogs/stat/ProximaNova-Bold.otf", welcome_size)
    while font_name.getsize(text_welcome)[0] < 500:
        welcome_size += 1
        font_welcome = ImageFont.truetype("cogs/stat/ProximaNova-Bold.otf", welcome_size)
        if welcome_size == 71:
            break
    welcome_size -= 1
    font_welcome = ImageFont.truetype("cogs/stat/ProximaNova-Bold.otf", welcome_size)

    text_name = u"{}".format(user.display_name+"#"+user.discriminator)
    name_size = 1
    font_name = ImageFont.truetype("cogs/stat/ProximaNova-Regular.ttf", name_size)
    while font_name.getsize(text_name)[0] < 500:
        name_size += 1
        font_name = ImageFont.truetype("cogs/stat/ProximaNova-Regular.ttf", name_size)
        if name_size == 36:
            break
    name_size -= 1
    font_name = ImageFont.truetype("cogs/stat/ProximaNova-Regular.ttf", name_size)

    ava_url = user.avatar_url
    if not ava_url:
        ava_url = user.default_avatar_url
    response = requests.get(ava_url)
    avatar = Image.open(BytesIO(response.content))
    avatar = avatar.resize((343, 343))
    avatar.putalpha(mask)
    back.paste(under, (0, 0), under)
    back.paste(avatar, (29, 29), avatar)


    kernel = [
        0, 1, 2, 1, 0,
        1, 2, 4, 2, 1,
        2, 4, 8, 4, 1,
        1, 2, 4, 2, 1,
        0, 1, 2, 1, 0
    ]
    kernelsum = sum(kernel)
    myfilter = ImageFilter.Kernel((5, 5), kernel, scale = 0.3 * kernelsum)
    halo = Image.new('RGBA', back.size, (0, 0, 0, 0))
    ImageDraw.Draw(halo).text(
        (435, 120),
        text_welcome,
        (0, 0, 0),
        font=font_welcome
    )
    ImageDraw.Draw(halo).text(
        (435, 230),
        text_name,
        (0, 0, 0),
        font=font_name
    )
    blurred_halo = halo.filter(myfilter)
    ImageDraw.Draw(blurred_halo).text(
        (435, 120),
        text_welcome,
        (color[0], color[1], color[2]),
        font=font_welcome
    )
    ImageDraw.Draw(blurred_halo).text(
        (435, 230),
        text_name,
        (color[0], color[1], color[2]),
        font=font_name
    )
    back = Image.composite(back, blurred_halo, ImageChops.invert(blurred_halo))
    draw = ImageDraw.Draw(back)

    filename = 'cogs/stat/return/welcome/{}.png'.format(user.server.id+'_'+user.id)
    back.save(filename)
    content=None
    if const["welcome_text"]:
        content = welcomer_format(const["welcome_text"], user)
    await client.send_file(channel, filename, content=content)
    os.remove(filename)
    return

async def tomori_log_ban(client, member, SHARD_ID):
    server = member.server
    payload = {
        "author": {
            "name": "Ban {type} | Shard #{id}".format(
                type="bot" if member.bot else "user",
                id=SHARD_ID
            ),
            "icon_url": beauty_icon(server.icon_url if server.icon_url else client.user.default_avatar_url, "png")
        },
        "color": 15794456,
        "thumbnail": beauty_icon(member.avatar_url if member.avatar_url else client.user.default_avatar_url, "png"),
        "footer": {
            "text": "ID: {0.id}".format(member)
        },
        "timestamp": datetime.utcnow(),
        "fields": [
            {
                "name": "User",
                "value": tagged_name(member),
                "inline": True
            },
            {
                "name": "Mention",
                "value": member.mention,
                "inline": True
            },
            {
                "name": "Server",
                "value": server.name+"\n"+server.id,
                "inline": True
            },
            {
                "name": "Reason",
                "value": "'Event references'",
                "inline": True
            }
        ]
    }
    if member.id == client.user.id:
        payload["text"] = "<@&479244721542266933>"
    msg = Webhook(web_url=wh_log_url["events"], **payload)
    await msg.post()

async def tomori_log_unban(client, server, user, SHARD_ID):
    payload = {
        "author": {
            "name": "Unban {type} | Shard #{id}".format(
                type="bot" if user.bot else "user",
                id=SHARD_ID
            ),
            "icon_url": beauty_icon(server.icon_url if server.icon_url else client.user.default_avatar_url, "png")
        },
        "color": 15794456,
        "thumbnail": beauty_icon(user.avatar_url if user.avatar_url else client.user.default_avatar_url, "png"),
        "footer": {
            "text": "ID: {0.id}".format(user)
        },
        "timestamp": datetime.utcnow(),
        "fields": [
            {
                "name": "User",
                "value": tagged_name(user),
                "inline": True
            },
            {
                "name": "Mention",
                "value": user.mention,
                "inline": True
            },
            {
                "name": "Server",
                "value": server.name+"\n"+server.id,
                "inline": True
            },
            {
                "name": "Reason",
                "value": "'Event references'",
                "inline": True
            }
        ]
    }
    msg = Webhook(web_url=wh_log_url["events"], **payload)
    await msg.post()

async def u_verify(client, conn, context, identify):
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
    if not const:
        em.description = locale[lang]["global_not_available"].format(who=message.author.display_name+"#"+message.author.discriminator)
        await client.send_message(message.channel, embed=em)
        return
    em = discord.Embed(colour=int(const["em_color"], 16) + 512)
    try:
        await client.delete_message(message)
    except:
        pass
    identify = clear_name(identify)
    who = discord.utils.get(message.server.members, name=identify)
    if not who:
        identify = re.sub(r'[<@#&!>]+', '', identify.lower())
        who = discord.utils.get(message.server.members, id=identify)
    if not who:
        em.description = locale[lang]["incorrect_argument"].format(
            who=message.author.display_name+"#"+message.author.discriminator,
            arg="user"
        )
        await client.send_message(message.channel, embed=em)
        return
    dat = await conn.fetchrow("SELECT * FROM mods WHERE type = 'badges' AND name = '{member}'".format(member=who.id))
    badges = ["verified"]
    if dat:
        for badge in dat["arguments"]:
            if badge in badges_list and not badge == "verified":
                badges.append(badge)
        await conn.execute("UPDATE mods SET arguments=ARRAY['{args}'] WHERE type = 'badges' AND name = '{name}'".format(
            name=who.id,
            args="', '".join(badges)
        ))
    else:
        await conn.execute("INSERT INTO mods(name, type, arguments) VALUES('{name}', 'badges', ARRAY['{args}'])".format(
            name=who.id,
            args="', '".join(badges)
        ))
    em.description = locale[lang]["user_verified"].format(name=who.display_name+"#"+who.discriminator)
    try:
        await client.send_message(who, embed=em)
    except:
        await client.send_message(message.channel, embed=em)
    return


spam_messages = {}


antispam_channels = [
"516677174523330580",
"509819239499038720"
]

async def check_spam(client, conn, const, message):
    text = message.content
    author = message.author
    if message.server.id == '485400595235340303' and not message.channel.id in antispam_channels:
        return
    if author.id == message.server.owner.id or any(role.permissions.administrator for role in author.roles):
        return
    lang = const["locale"]
    if not lang in locale.keys():
        return
    em = discord.Embed(
        title="Tomori ANTISPAM",
        colour=int(const["em_color"], 16) + 512
    )
    # Links
    if const["antispam_url"]:
        urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text)
        if "discord.gg" in text.lower():
            urls.append(1)
        if urls:
            em.description = locale[lang]["antispam_url"].format(
                who=message.author.display_name+"#"+message.author.discriminator,
                server=message.server
            )
            await asyncio.wait([
                client.delete_message(message),
                client.send_message(message.author, embed=em)
            ])
            return True

    # Spam
    global spam_messages
    if const["antispam_spam"]:
        user = spam_messages.get(author.id)
        _time = datetime.now()
        if not user or (_time - user.get("first_message_time")).seconds > 5:
            spam_messages.update({
                author.id: {
                    "messages": [
                        message
                    ],
                    "first_message_time": _time
                }
            })
            return False
        elif len(user.get("messages")) > 5:
            em.description = locale[lang]["antispam_spam"].format(who=message.author.display_name+"#"+message.author.discriminator)
            role = discord.utils.get(message.server.roles, id=const["antispam_role_id"])
            roles = author.roles
            if role:
                roles.append(role)
            mess = user.get("messages")
            try:
                spam_messages.pop(author.id)
            except:
                pass
            await asyncio.wait([
                client.delete_messages(mess),
                client.send_message(message.author, embed=em),
                client.replace_roles(author, *roles)
            ])
            await asyncio.sleep(600)
            await client.remove_roles(author, role)
            return True
        else:
            mess = user.get("messages")
            mess.append(message)
            spam_messages.update({
                author.id: {
                    "messages": mess,
                    "first_message_time": user.get("first_message_time")
                }
            })

    # Mentions
    if len(message.mentions) + len(message.role_mentions) > 4:
        em.description = locale[lang]["antispam_spam"].format(who=message.author.display_name+"#"+message.author.discriminator)
        role = discord.utils.get(message.server.roles, id=const["antispam_role_id"])
        roles = author.roles
        if role:
            roles.append(role)
        await asyncio.wait([
            client.delete_message(message),
            client.send_message(message.author, embed=em),
            client.replace_roles(author, *roles)
        ])
        await asyncio.sleep(300)
        await client.remove_roles(author, role)

    # End
    return False


def add_muted(client, user_dat):
    global muted_users
    t = int(user_dat["condition"])
    s = client.get_server(user_dat["server_id"])
    if s:
        m = s.get_member(user_dat["name"])
        if m:
            o = {
                "server": s,
                "member": m,
                "type": user_dat["value"]
            }
            if t in muted_users.keys():
                muted_users[t].append(o)
            else:
                muted_users[t] = [o]
            return True
    return False

async def u_unmute(client, conn, server, member):
    const = await get_cached_server(conn, server.id)
    if not const["antispam_role_id"]:
        return
    role = discord.utils.get(server.roles, id=const["antispam_role_id"])
    if not role:
        return
    await conn.execute("DELETE FROM mods WHERE type = 'muted_users' AND server_id = '{server}' AND name = '{member}'".format(
        server=server.id,
        member=member.id
    ))
    await client.remove_roles(member, role)


async def add_follow_links(client, message, const, em):
    lang = const["locale"]
    if message.server.id == old_neko_id:
        #url = await u_invite_to_server(client, new_neko_id)
        url = "https://discord.gg/yEczRp6"
        em.add_field(
            name="Neko.land переехал!",
            value=url,
            inline=False
        )
    else:
        em.add_field(
            name=locale[lang]["global_follow_us"],
            value=tomori_links,
            inline=False
        )
    return em


# async def u_check_achievements(client, conn, const, message, key):
#     lang = const["locale"]
#     if not lang in locale.keys():
#         return
#     em = discord.Embed(colour=int(const["em_color"], 16) + 512)
#     em.description = locale[lang]["lvlup"].format(
#         who=who.mention,
#         lvl=xp_lvlup_list[xp]
#     )
#     em.set_image(url=lvlup_image_url)
#     try:
#         msg = await client.send_message(channel, embed=em)
#         await asyncio.sleep(25)
#         await client.delete_message(msg)
#     except:
#         pass
