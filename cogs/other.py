import discord
import asyncio
import requests
import time
from datetime import datetime, date
import string
import random
import copy
import re
import json
import asyncpg
from discord.ext import commands
from cogs.locale import *
from cogs.const import *
from cogs.help import *

support_url = "https://discord.gg/tomori"
site_url = "http://discord.band"
site_commands_url = "https://discord.band/commands"
invite_url = "https://discordapp.com/api/oauth2/authorize?client_id=491605739635212298&permissions=536341719&redirect_uri=https%3A%2F%2Fdiscord.band&scope=bot"


async def o_about(client, conn, context):
    message = context.message
    server_id = message.server.id
    const = await conn.fetchrow("SELECT em_color, locale FROM settings WHERE discord_id = '{discord_id}'".format(discord_id=server_id))
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
    try:
        await client.delete_message(message)
    except:
        pass
    em = discord.Embed(colour=int(const["em_color"], 16) + 512)
    if const["locale"] == "english":
        em.description = "***Python-bot created by __Ананасовая Печенюха (Cookie)__\n\
supported by __Unknown__ and __Teris__.***\n\n\
**[Support server]({support_url})**\n\
**[Site]({site_url})**\n\n\
For any questions talk to <@316287332779163648>.".format(support_url=support_url, site_url=site_url)
    else:
        em.description = "***Python-bot написанный __Ананасовой Печенюхой__\n\
при поддержке __Unknown'a__ и __Teris'а__.***\n\n\
**[Ссылка на сервер поддержки]({support_url})**\n\
**[Ссылка на сайт]({site_url})**\n\n\
По всем вопросам обращайтесь к <@316287332779163648>.".format(support_url=support_url, site_url=site_url)
    em.add_field(
        name="Поддержать Томори",
        value=tomori_links,
        inline=False
    )
    await client.send_message(message.channel, embed=em)
    return

async def o_invite(client, conn, context):
    message = context.message
    server_id = message.server.id
    const = await conn.fetchrow("SELECT em_color, locale FROM settings WHERE discord_id = '{discord_id}'".format(discord_id=server_id))
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
    try:
        await client.delete_message(message)
    except:
        pass
    em = discord.Embed(colour=int(const["em_color"], 16) + 512)
    em.title = "Ссылка для приглашения Tomori:"
    em.description = invite_url
    em.add_field(
        name="Поддержать Томори",
        value=tomori_links,
        inline=False
    )
    await client.send_message(message.author, embed=em)
    return

async def o_server(client, conn, context):
    message = context.message
    server_id = message.server.id
    server = message.server
    const = await conn.fetchrow("SELECT em_color, prefix, locale FROM settings WHERE discord_id = '{}'".format(server_id))
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
    try:
        await client.delete_message(message)
    except:
        pass
    em = discord.Embed(colour=int(const["em_color"], 16) + 512)
    em.set_author(name=server.name, icon_url=server.icon_url)
    em.add_field(
        name=":crown:Владелец",
        value="{0.name}#{0.discriminator}".format(server.owner),
        inline=True
    )
    em.add_field(
        name=":point_right:Префикс",
        value=const[1],
        inline=True
    )
    em.add_field(
        name=":tv:Каналы",
        value=str(len(server.channels)),
        inline=True
    )
    em.add_field(
        name=":person_with_pouting_face:Пользователи",
        value=str(len(server.members)),
        inline=True
    )
    em.add_field(
        name=":hourglass:Возраст",
        value="{} дней".format(int((datetime.utcnow() - server.created_at).days)),
        inline=True
    )
    em.add_field(
        name=":satellite:ID",
        value=server.id,
        inline=True
    )
    em.add_field(
        name=":smiley:Emoji",
        value=str(len(server.emojis)),
        inline=True
    )
    em.set_image(url=message.server.icon_url)
    await client.send_message(message.channel, embed=em)
    return

async def o_avatar(client, conn, context, who):
    message = context.message
    server_id = message.server.id
    const = await conn.fetchrow("SELECT em_color, is_avatar, locale FROM settings WHERE discord_id = '{discord_id}'".format(discord_id=server_id))
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
    if not who:
        who = message.author
    em.title = "Аватар {}".format(clear_name(who.display_name[:50]))
    em.set_image(url=who.avatar_url)
    await client.send_message(message.channel, embed=em)
    return

async def o_like(client, conn, context):
    message = context.message
    server_id = message.server.id
    if message.author.bot or message.channel.is_private:
        return
    const = await conn.fetchrow("SELECT em_color, locale, likes, like_one, like_time FROM settings WHERE discord_id = '{discord_id}'".format(discord_id=server_id))
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
    now = int(time.time())
    if now - const["like_time"] > 14400:
        await conn.execute("UPDATE settings SET likes = {likes}, like_time = {like_time} WHERE discord_id = '{discord_id}'".format(
            likes=const["likes"] + const["like_one"],
            like_time=now,
            discord_id=server_id
        ))
        global top_servers
        top_servers = await conn.fetch("SELECT discord_id FROM settings ORDER BY likes DESC, like_time ASC LIMIT 10")
        em.description = locale[lang]["other_like_success"].format(who=message.author.display_name+"#"+message.author.discriminator)
    else:
        t=14400 - now + const["like_time"]
        h=str(t//3600)
        m=str((t//60)%60)
        s=str(t%60)
        em.description = locale[lang]["other_like_wait"].format(
            who=message.author.display_name+"#"+message.author.discriminator,
            hours=h,
            minutes=m,
            seconds=s
            )
        em.add_field(
            name="Поддержать Томори",
            value=tomori_links,
            inline=False
        )
    await client.send_message(message.channel, embed=em)
    return

async def o_list(client, conn, context, page):
    message = context.message
    server_id = message.server.id
    if message.author.bot or message.channel.is_private:
        return
    const = await conn.fetchrow("SELECT em_color, locale FROM settings WHERE discord_id = '{discord_id}'".format(discord_id=server_id))
    lang = const["locale"]
    if not lang in locale.keys():
        em = discord.Embed(description="{who}, {response}.".format(
            who=message.author.display_name+"#"+message.author.discriminator,
            response="ошибка локализации",
            colour=0xC5934B))
        await client.send_message(message.channel, embed=em)
        return
    _locale = locale[lang]
    em = discord.Embed(colour=0x87b5ff)
    if not const:
        em.description = _locale["global_not_available"].format(who=message.author.display_name+"#"+message.author.discriminator)
        await client.send_message(message.channel, embed=em)
        return
    try:
        await client.delete_message(message)
    except:
        pass
    dat = await conn.fetchrow("SELECT COUNT(name) FROM settings")
    all_count = dat[0]
    pages = (((all_count - 1) // 10) + 1)
    if not page:
        page = 1
    if page > pages:
        em.description = _locale["global_page_not_exists"].format(who=message.author.display_name+"#"+message.author.discriminator, number=page)
        await client.send_message(message.channel, embed=em)
        return
    em.title = _locale["other_top_of_servers"]
    if all_count == 0:
        em.description = _locale["global_list_is_empty"]
        await client.send_message(message.channel, embed=em)
        return
    dat = await conn.fetch("SELECT name, discord_id, likes FROM settings ORDER BY likes DESC, like_time ASC LIMIT 10 OFFSET {offset}".format(offset=(page-1)*10))
    for index, server in enumerate(dat):
        member_count = 0
        serv = client.get_server(server["discord_id"])
        if serv:
            member_count = serv.member_count
        em.add_field(
            name="#{index} {name}".format(
                index=(page-1)*10+index+1,
                name=server["name"]
            ),
            value="<:likes:493040819402702869>\xa0{likes}\xa0\xa0<:users:492827033026560020>\xa0{member_count}\xa0\xa0[<:server:492861835087708162>](https://discord-server.com/{id})".format(
                likes=server["likes"],
                member_count=member_count,
                id=server["discord_id"],
            ),
            inline=True
        )
    em.set_footer(text=_locale["other_footer_page"].format(number=page, length=pages))
    await client.send_message(message.channel, embed=em)
    return

async def o_report(client, conn, context):
    message = context.message
    server_id = message.server.id
    const = await conn.fetchrow("SELECT em_color, locale FROM settings WHERE discord_id = '{}'".format(server_id))
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
    for s in admin_list:
        try:
            await client.send_message(discord.utils.get(message.server.members, id=s), "[server - {}, id - {}] (chat - {}, id - {}) <name - {}, id - {}, display_name - {}> <=> {}".format(message.server.name, message.server.id, message.channel.name, message.channel.id, message.author.display_name[:50], message.author.id, message.author.display_name, message.content))
        except:
            pass
    em.title='{} отправил репорт!'.format(message.author.display_name+"#"+message.author.discriminator)
    em.set_image(url='https://media.giphy.com/media/xTkcESPybY7bmlKL7O/giphy.gif')
    await client.send_message(message.channel, embed=em)
    return

async def o_ping(client, conn, context):
    message = context.message
    server_id = message.server.id
    const = await conn.fetchrow("SELECT em_color, locale FROM settings WHERE discord_id = '{}'".format(server_id))
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
    now = datetime.utcnow()
    delta = now - message.timestamp
    latency = delta.microseconds / 1000
    em.description=locale[lang]["other_ping"].format(
        who=message.author.display_name+"#"+message.author.discriminator,
        latency=int(latency)
        )
    await client.send_message(message.channel, embed=em)
    return

async def o_help(client, conn, context):
    message = context.message
    server_id = message.server.id
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
    if message.content.startswith(const["prefix"]+"help "):
        await h_check_help(client, message, locale[lang], em, const["prefix"])
        return
    em.title = "Команды бота Tomori"
    em.description = "Префикс для сервера ``{}:``  {}".format(const["name"], const["prefix"])
    com_adm = ""
    com_econ = ""
    com_fun = ""
    com_stat = ""
    com_other = ""
    com_mon = ""
    if const["is_say"]:
        com_adm += "``say``, ``say_embed``, "
    if const["is_clear"]:
        com_adm += "``clear``, "
    if const["is_sex"]:
        com_fun += "``sex``, "
    if const["is_kick"]:
        com_adm += "``kick``, "
    if const["is_ban"]:
        com_adm += "``ban``, ``unban``, "
    if const["is_timely"]:
        com_econ += "``timely``, "
    if const["is_work"]:
        com_econ += "``work``, "
    if const["is_br"]:
        com_econ += "``br``, "
    if const["is_slots"]:
        com_econ += "``slots``, "
    if const["is_give"]:
        com_econ += "``give``, "
    if const["is_kiss"]:
        com_fun += "``kiss``, "
    if const["is_hug"]:
        com_fun += "``hug``, "
    if const["is_punch"]:
        com_fun += "``punch``, "
    if const["is_five"]:
        com_fun += "``five``, "
    if const["is_wink"]:
        com_fun += "``wink``, "
    if const["is_fuck"]:
        com_fun += "``fuck``, "
    if const["is_drink"]:
        com_fun += "``drink``, "
    if const["is_rep"]:
        com_fun += "``rep``, "
    if const["is_cash"]:
        com_stat += "``$``, "
    if const["is_top"]:
        com_stat += "``top``, "
    if const["is_me"]:
        com_stat += "``me``, "
    com_other = "``help``, ``ping``, "
    if const["is_avatar"]:
        com_other += "``avatar``, "
    com_other += "``report``, ``server``, ``invite``, ``about``, "
    com_adm += "``start``, ``stop``, "
    com_mon += "``like``, ``list``, "
    if com_adm != "":
        em.add_field(name="Admin", value=com_adm[:-2], inline=False)
    if com_econ != "":
        em.add_field(name="Economics", value=com_econ[:-2], inline=False)
    if com_fun != "":
        em.add_field(name="Fun", value=com_fun[:-2], inline=False)
    if com_stat != "":
        em.add_field(name="Stats", value=com_stat[:-2], inline=False)
    if com_mon != "":
        em.add_field(name="Monitoring", value=com_mon[:-2], inline=False)
    if com_other != "":
        em.add_field(name="Other", value=com_other[:-2], inline=False)
    em.add_field(name=locale[lang]["help_more_info"], value=site_commands_url, inline=False)
    em.set_footer(text=locale[lang]["help_help_by_command"].format(prefix=const["prefix"]))
    await client.send_message(message.channel, embed=em)
    return

async def o_backgrounds(client, conn, context):
    message = context.message
    server_id = message.server.id
    const = await conn.fetchrow("SELECT server_money, em_color, locale FROM settings WHERE discord_id = '{}'".format(server_id))
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
    em.title = locale[lang]["other_backgrounds_title"]
    if len(background_list) == 0:
        em.description = locale[lang]["other_backgrounds_list_is_empty"]
        await client.send_message(message.channel, embed=em)
        return
    for i, back in enumerate(background_name_list):
        em.add_field(
            name=locale[lang]["other_backgrounds_element"].format(
                position=i+1,
                name=back
            ),
            value="-------------------------",
            inline=True
        )
    await client.send_message(message.channel, embed=em)
    return

async def o_set(client, conn, context, arg1, arg2, args):
    message = context.message
    server_id = message.server.id
    const = await conn.fetchrow("SELECT em_color, locale, server_money FROM settings WHERE discord_id = '{}'".format(server_id))
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

    if arg1 == "background" or arg1 == "back":
        if not arg2:
            em.description = locale[lang]["other_missed_argument"].format(
                who=message.author.display_name+"#"+message.author.discriminator,
                arg="name"
            )
            await client.send_message(message.channel, embed=em)
            return
        if args:
            arg2 = arg2 + " " + args
        if arg2.isdigit() and int(arg2) <= len(background_list) and int(arg2) > 0:
            arg2 = background_list[int(arg2)-1]
        else:
            arg2 = arg2.lower().replace(" ", "_") + ".jpg"
        if not arg2 in background_list:
            em.description = locale[lang]["other_incorrect_argument"].format(
                who=message.author.display_name+"#"+message.author.discriminator,
                arg="name"
            )
            await client.send_message(message.channel, embed=em)
            return
        dat = await conn.fetchrow("SELECT cash, background FROM users WHERE discord_id = '{}'".format(message.author.id))
        if dat:
            if dat[0] < background_change_price:
                em.description = locale[lang]["global_dont_have_that_much_money"].format(who=message.author.display_name+"#"+message.author.discriminator, money=const[2])
                await client.send_message(message.channel, embed=em)
                return
            if dat[1] == arg2:
                em.description = locale[lang]["other_backgrounds_already_has"].format(who=message.author.display_name+"#"+message.author.discriminator)
                await client.send_message(message.channel, embed=em)
                return
            await conn.execute("UPDATE users SET cash = {cash}, background = '{back}' WHERE discord_id = '{id}'".format(
                cash=dat[0] - background_change_price,
                back=arg2,
                id=message.author.id
            ))
            em.description = locale[lang]["other_backgrounds_success_response"].format(
                who=message.author.display_name+"#"+message.author.discriminator
            )
        else:
            await conn.execute("INSERT INTO users(name, discord_id) VALUES('{}', '{}')".format(clear_name(message.author.display_name[:50]), message.author.id))
            em.description = locale[lang]["global_dont_have_that_much_money"].format(who=message.author.display_name+"#"+message.author.discriminator, money=const[1])
        await client.send_message(message.channel, embed=em)
        return

    if arg1 == "prefix":
        if not message.author == message.server.owner and not any(role.permissions.administrator for role in message.author.roles):
            em.description = locale[lang]["global_not_allow_to_use"].format(
                who=message.author.display_name+"#"+message.author.discriminator
            )
            await client.send_message(message.channel, embed=em)
            return
        if not arg2:
            em.description = locale[lang]["other_missed_argument"].format(
                who=message.author.display_name+"#"+message.author.discriminator,
                arg="prefix"
            )
            em.description += "\n"+locale[lang]["other_set_prefix_you_can_try"]+" `%s`" % "`, `".join(prefix_list)
            await client.send_message(message.channel, embed=em)
            return
        if arg2 in prefix_list:
            await conn.execute("UPDATE settings SET prefix = '{}' WHERE discord_id = '{}'".format(arg2,server_id))
            em.description = locale[lang]["other_set_prefix_success"].format(
                who=message.author.display_name+"#"+message.author.discriminator,
                prefix=arg2
            )
            await client.send_message(message.channel, embed=em)
            return
        elif arg2 == "default":
            await conn.execute("UPDATE settings SET prefix = '{}' WHERE discord_id = '{}'".format('!',server_id))
            em.description = locale[lang]["other_set_prefix_success"].format(
                who=message.author.display_name+"#"+message.author.discriminator,
                prefix='!'
            )
            em.description += "\n" + locale[lang]["other_set_prefix_you_can_try"] + " `%s`" % "`, `".join(prefix_list)
        else:
            em.description = locale[lang]["other_set_prefix_you_can_try"] + " `%s`" % "`, `".join(prefix_list)
        await client.send_message(message.channel, embed=em)
        return

    if arg1 == "autorole":
        if not message.author == message.server.owner and not any(role.permissions.administrator for role in message.author.roles):
            em.description = locale[lang]["global_not_allow_to_use"].format(
                who=message.author.display_name+"#"+message.author.discriminator
            )
            await client.send_message(message.channel, embed=em)
            return
        if not arg2:
            em.description = locale[lang]["other_missed_argument"].format(
                who=message.author.display_name+"#"+message.author.discriminator,
                arg="name"
            )
            await client.send_message(message.channel, embed=em)
            return
        if args:
            arg2 = arg2 + " " + args
        _roles = message.server.roles
        roles = []
        for role  in _roles:
            roles.append(role.id)
        arg2 = re.sub(r'[<@#&!>]+', '', arg2.lower())
        if not arg2.isdigit() or not arg2 in roles:
            em.description = locale[lang]["other_incorrect_argument"].format(
                who=message.author.display_name+"#"+message.author.discriminator,
                arg="name"
            )
            await client.send_message(message.channel, embed=em)
            return
        dat = await conn.fetchrow("SELECT prefix FROM settings WHERE discord_id = '{}'".format(message.server.id))
        if dat:
            await conn.execute("UPDATE settings SET autorole_id = '{role_id}' WHERE discord_id = '{server_id}'".format(
                role_id=arg2,
                server_id=message.server.id
            ))
        else:
            await conn.execute("INSERT INTO settings(name, discord_id, autorole_id) VALUES('{name}', '{id}', '{role}')".format(
                name=clear_name(message.server.name[:50]),
                id=message.server.id,
                role=arg2
            ))
        em.description = locale[lang]["other_autorole_success_response"].format(
            who=message.author.display_name+"#"+message.author.discriminator,
            role_id=arg2
        )
        await client.send_message(message.channel, embed=em)
        return



    if arg1 == "language" or arg1 == "lang":
        if not message.author == message.server.owner and not any(role.permissions.administrator for role in message.author.roles):
            em.description = locale[lang]["global_not_allow_to_use"].format(
                who=message.author.display_name+"#"+message.author.discriminator
            )
            await client.send_message(message.channel, embed=em)
            return
        if not arg2:
            em.description = locale[lang]["other_missed_argument"].format(
                who=message.author.display_name+"#"+message.author.discriminator,
                arg="name"
            )
            await client.send_message(message.channel, embed=em)
            return
        if args:
            arg2 = arg2 + " " + args
        if not arg2 in locale.keys():
            em.description = locale[lang]["other_incorrect_argument"].format(
                who=message.author.display_name+"#"+message.author.discriminator,
                arg="name"
            )
            await client.send_message(message.channel, embed=em)
            return
        dat = await conn.fetchrow("SELECT prefix FROM settings WHERE discord_id = '{}'".format(message.server.id))
        if dat:
            await conn.execute("UPDATE settings SET locale = '{lang}' WHERE discord_id = '{server_id}'".format(
                lang=arg2,
                server_id=message.server.id
            ))
        else:
            await conn.execute("INSERT INTO settings(name, discord_id, locale) VALUES('{name}', '{id}', '{lang}')".format(
                name=clear_name(message.server.name[:50]),
                id=message.server.id,
                lang=arg2
            ))
        em.description = locale[arg2]["other_lang_success_response"].format(
            who=message.author.display_name+"#"+message.author.discriminator,
            lang=arg2
        )
        await client.send_message(message.channel, embed=em)
        return


    if not arg1:
        em.description = locale[lang]["other_missed_argument"].format(
            who=message.author.display_name+"#"+message.author.discriminator,
            arg="category"
        )
        await client.send_message(message.channel, embed=em)
        return

    em.description = locale[lang]["other_incorrect_argument"].format(
        who=message.author.display_name+"#"+message.author.discriminator,
        arg="category"
    )
    await client.send_message(message.channel, embed=em)
    return
