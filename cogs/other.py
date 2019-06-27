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
from bs4 import BeautifulSoup
from discord.ext import commands
from cogs.locale import *
from cogs.const import *
from cogs.help import *
from cogs.ids import *
from cogs.util import *
from cogs.discord_hooks import Webhook
from config.constants import *

support_url = "https://discord.gg/tomori"
site_url = "http://discord.band"
site_commands_url = "https://discord.band/commands"
invite_url = "https://discordapp.com/api/oauth2/authorize?client_id=491605739635212298&permissions=536341719&redirect_uri=https%3A%2F%2Fdiscord.band&scope=bot"



async def o_webhook(client, conn, context, name, value):
    message = context.message
    server_id = message.server.id
    const = await get_cached_server(conn, server_id)
    lang = const["locale"]
    em = discord.Embed(colour=0xC5934B)
    if not lang in locale.keys():
        em.description = "{who}, {response}.".format(who=tagged_dname(message.author), response="ошибка локализации")
        await client.send_message(message.channel, embed=em)
        return
    if not const:
        em.description = locale[lang]["global_not_available"].format(who=tagged_dname(message.author))
        await client.send_message(message.channel, embed=em)
        return
    em = discord.Embed(colour=int(const["em_color"], 16) + 512)
    dat = await conn.fetchrow("SELECT * FROM mods WHERE type = 'webhook' AND name = '{name}' AND server_id = '{server_id}'".format(server_id=server_id, name=clear_name(name).lower()))
    if not dat:
        em.description = locale[lang]["other_webhook_not_exists"].format(
            who=tagged_dname(message.author),
            name=name
        )
        await client.send_message(message.channel, embed=em)
        return
    if dat["condition"]:
        cond = dat["condition"]
    else:
        cond = ""
    if not any(cond==role.id or role.permissions.administrator for role in message.author.roles) and not cond==message.author.id and not message.author.id == message.server.owner.id:
        return
    try:
        await client.delete_message(message)
    except:
        pass
    try:
        ret = json.loads(value)
        if ret and isinstance(ret, dict):
            msg = Webhook(web_url=dat["value"], **ret)
            await msg.post()
        else:
            msg = Webhook(
                web_url=dat["value"],
                text=value
            )
            await msg.post()
    except:
        msg = Webhook(
            web_url=dat["value"],
            text=value
        )
        await msg.post()

async def o_about(client, conn, context):
    message = context.message
    server_id = message.server.id
    const = await get_cached_server(conn, server_id)
    lang = const["locale"]
    em = discord.Embed(colour=0xC5934B)
    if not lang in locale.keys():
        em.description = "{who}, {response}.".format(who=tagged_dname(message.author), response="ошибка локализации")
        await client.send_message(message.channel, embed=em)
        return
    if not const:
        em.description = locale[lang]["global_not_available"].format(who=tagged_dname(message.author))
        await client.send_message(message.channel, embed=em)
        return
    try:
        await client.delete_message(message)
    except:
        pass
    em = discord.Embed(colour=int(const["em_color"], 16) + 512)
    if const["locale"] == "english":
        em.description = "***Python-bot created by __Pineapple Cookie#0373__\n\
supported by __Unknown__ and __Teris__.***\n\n\
**[Support server]({support_url})**\n\
**[Site]({site_url})**\n\n\
For any questions talk to <@499937748862500864>.".format(support_url=support_url, site_url=site_url)
    else:
        em.description = "***Python-bot написанный __Ананасовой Печенюхой__\n\
при поддержке __Unknown'a__ и __Teris'а__.***\n\n\
**[Ссылка на сервер поддержки]({support_url})**\n\
**[Ссылка на сайт]({site_url})**\n\n\
По всем вопросам обращайтесь к <@499937748862500864>.".format(support_url=support_url, site_url=site_url)
    if not message.server.id in servers_without_follow_us:
        em = await add_follow_links(client, message, const, em)
    await client.send_message(message.channel, embed=em)
    return

async def o_invite(client, conn, context):
    message = context.message
    server_id = message.server.id
    const = await get_cached_server(conn, server_id)
    lang = const["locale"]
    em = discord.Embed(colour=0xC5934B)
    if not lang in locale.keys():
        em.description = "{who}, {response}.".format(who=tagged_dname(message.author), response="ошибка локализации")
        await client.send_message(message.channel, embed=em)
        return
    if not const:
        em.description = locale[lang]["global_not_available"].format(who=tagged_dname(message.author))
        await client.send_message(message.channel, embed=em)
        return
    try:
        await client.delete_message(message)
    except:
        pass
    em = discord.Embed(colour=int(const["em_color"], 16) + 512)
    em.title = locale[lang]["other_invite_title"]
    em.description = invite_url
    if not message.server.id in servers_without_follow_us:
        em = await add_follow_links(client, message, const, em)
    await client.send_message(message.author, embed=em)
    return



standart = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"

def clear_code(code_):
    _code = ""
    for symbol in code_:
        if symbol in standart:
            _code = _code + symbol
    return _code[:8]

def generate_code():
    i = 0
    code_ = ""
    while i < 8:
        i += 1
        code_ = code_ + random.choice(standart)
    return code_

async def o_inv(client, conn, context, code, name):
    message = context.message
    server_id = message.server.id
    const = await get_cached_server(conn, server_id)
    lang = const["locale"]
    em = discord.Embed(colour=0xC5934B)
    if not lang in locale.keys():
        em.description = "{who}, {response}.".format(who=tagged_dname(message.author), response="ошибка локализации")
        await client.send_message(message.channel, embed=em)
        return
    if not const:
        em.description = locale[lang]["global_not_available"].format(who=tagged_dname(message.author))
        await client.send_message(message.channel, embed=em)
        return

    inv = await client.get_invite(code)
    if not inv:
        em.description = locale[lang]["not_invite"].format(who=tagged_dname(message.author))
        await client.send_message(message.channel, embed=em)
        return
    inv = "https://discord.gg/{}".format(inv.code)

    codes = await conn.fetch("SELECT name FROM mods WHERE type='custom_invite'")

    def check_code(code_):
        return any(code_ == _code["name"] for _code in codes)

    if not name:
        name = generate_code()
        while check_code(name):
            name = generate_code()
    else:
        name = clear_code(name.lower())
        if len(name) < 3:
            em.description = locale[lang]["invite_cant_be_less"].format(who=tagged_dname(message.author))
            await client.send_message(message.channel, embed=em)
            return
        if check_code(name):
            em.description = locale[lang]["invite_taken"].format(who=tagged_dname(message.author), invite=name)
            await client.send_message(message.channel, embed=em)
            return

    em = discord.Embed(colour=int(const["em_color"], 16) + 512)
    em.description = locale[lang]["invite_successfully_installed"].format(who=tagged_dname(message.author), invite=name)

    if not message.server.id in servers_without_follow_us:
        em = await add_follow_links(client, message, const, em)
    await asyncio.wait([
        client.send_message(message.channel, embed=em),
        client.delete_message(message),
        conn.execute("INSERT INTO mods(server_id, name, type, value, condition) VALUES('{server}', '{code}', 'custom_invite', '{url}', '{who}')".format(
            server=server_id,
            code=name,
            url=inv,
            who="{} [{}]".format(tagged_name(message.author), message.author.id)
        ))
    ])
    return

async def o_server(client, conn, context):
    message = context.message
    server_id = message.server.id
    server = message.server
    const = await get_cached_server(conn, server_id)
    lang = const["locale"]
    em = discord.Embed(colour=0xC5934B)
    if not lang in locale.keys():
        em.description = "{who}, {response}.".format(who=tagged_dname(message.author), response="ошибка локализации")
        await client.send_message(message.channel, embed=em)
        return
    if not const:
        em.description = locale[lang]["global_not_available"].format(who=tagged_dname(message.author))
        await client.send_message(message.channel, embed=em)
        return
    try:
        await client.delete_message(message)
    except:
        pass
    em = discord.Embed(colour=int(const["em_color"], 16) + 512)
    name = server.name
    badges = ""
    if const["is_unverified"]:
        badges = "💩"
    else:
        if const["is_partner"]:
            badges += "<:partner:559064087699390524> "
        if const["is_nitro"]:
            badges += "<:nitro:528886245510742017> "
        if const["is_verified"]:
            badges += "<:verified:551470498920529921> "
    if not badges:
        badges = locale[lang]["no"]
    em.set_author(name=name, icon_url=server.icon_url)
    em.add_field(
        name=locale[lang]["other_server_owner"],
        value="{0.name}#{0.discriminator}".format(server.owner),
        inline=True
    )
    em.add_field(
        name=locale[lang]["other_server_prefix"],
        value=const["prefix"],
        inline=True
    )
    em.add_field(
        name=locale[lang]["other_server_badges"],
        value=badges,
        inline=True
    )
    em.add_field(
        name=locale[lang]["other_server_bank"],
        value=str(const["bank"]),
        inline=True
    )
    em.add_field(
        name=locale[lang]["other_server_channels"],
        value=str(len(server.channels)),
        inline=True
    )
    em.add_field(
        name=locale[lang]["other_server_members"],
        value=str(len(server.members)),
        inline=True
    )
    em.add_field(
        name=locale[lang]["other_server_lifetime"],
        value=locale[lang]["other_server_days"].format(int((datetime.utcnow() - server.created_at).days)),
        inline=True
    )
    em.add_field(
        name=":satellite:ID",
        value=server.id,
        inline=True
    )
    em.add_field(
        name=locale[lang]["other_server_emojis"],
        value=str(len(server.emojis)),
        inline=True
    )
    icon_url = message.server.icon_url
    if not icon_url:
        icon_url = client.user.default_avatar_url
    else:
        icon_url = "https://cdn.discordapp.com/icons/{id}/{icon}.png".format(
            id=message.server.id,
            icon=message.server.icon
        )
    em.set_thumbnail(url=icon_url)
    await client.send_message(message.channel, embed=em)
    return

async def o_avatar(client, conn, context, who):
    message = context.message
    server_id = message.server.id
    const = await get_cached_server(conn, server_id)
    lang = const["locale"]
    em = discord.Embed(colour=0xC5934B)
    if not lang in locale.keys():
        em.description = "{who}, {response}.".format(who=tagged_dname(message.author), response="ошибка локализации")
        await client.send_message(message.channel, embed=em)
        return
    if not const:
        em.description = locale[lang]["global_not_available"].format(who=tagged_dname(message.author))
        await client.send_message(message.channel, embed=em)
        return
    em = discord.Embed(colour=int(const["em_color"], 16) + 512)
    try:
        await client.delete_message(message)
    except:
        pass
    if not who:
        who = message.author
    em.title = locale[lang]["other_avatar"].format(clear_name(who.display_name[:50]))
    em.set_image(url=who.avatar_url)
    await client.send_message(message.channel, embed=em)
    return


async def o_urban(client, conn, context, text):
    message = context.message
    server_id = message.server.id
    const = await get_cached_server(conn, server_id)
    lang = const["locale"]
    em = discord.Embed(colour=0xC5934B)
    if not lang in locale.keys():
        em.description = "{who}, {response}.".format(who=tagged_dname(message.author), response="ошибка локализации")
        await client.send_message(message.channel, embed=em)
        return
    if not const or not const["is_ud"]:
        em.description = locale[lang]["global_not_available"].format(who=tagged_dname(message.author))
        await client.send_message(message.channel, embed=em)
        return
    em = discord.Embed(colour=int(const["em_color"], 16) + 512)
    icon_url = message.author.avatar_url
    if not icon_url:
        icon_url = message.author.default_avatar_url
    em.set_footer(text=tagged_dname(message.author), icon_url=icon_url)

    text = clear_text(text[:256])
    url = ('https://www.urbandictionary.com/define.php')
    params = {
        "term": text
    }
    s = requests.session()
    s.headers.update({'Content-Type': 'application/json'})
    raw = s.get(url, params=params).text
    soup = BeautifulSoup(raw, 'html5lib')
    top = soup.find(class_="meaning")
    if not top:
        em.title = locale[lang]["error_title"]
        em.description = locale[lang]["other_urban_error"]
    else:
        definition = top.text.strip()
        if len(definition) > 1024:
            definition = definition[:1021]+"..."
        example = soup.find(class_="example").text.strip()
        if len(example) > 1024:
            example = example[:1021]+"..."
        em.set_author(
            name="Urban Dictionary",
            icon_url="https://apprecs.org/gp/images/app-icons/300/2f/info.tuohuang.urbandict.jpg"
        )
        em.title = text
        em.add_field(
            name=locale[lang]["other_urban_def"],
            value=definition,
            inline=False
        )
        em.add_field(
            name=locale[lang]["other_urban_example"],
            value=example,
            inline=False
        )

    await asyncio.wait([
        client.delete_message(message),
        client.send_message(message.channel, embed=em)
    ])
    return


async def o_roll(client, conn, context, one, two):
    message = context.message
    server_id = message.server.id
    const = await get_cached_server(conn, server_id)
    lang = const["locale"]
    em = discord.Embed(colour=0xC5934B)
    if not lang in locale.keys():
        em.description = "{who}, {response}.".format(who=tagged_dname(message.author), response="ошибка локализации")
        await client.send_message(message.channel, embed=em)
        return
    if not const or not const["is_roll"]:
        em.description = locale[lang]["global_not_available"].format(who=tagged_dname(message.author))
        await client.send_message(message.channel, embed=em)
        return
    em = discord.Embed(colour=int(const["em_color"], 16) + 512)
    temp = max([one, two])
    one = min([one, two])
    two = temp
    count = random.randint(one, two)
    em.description = locale[lang]["other_roll_response"].format(
        who=tagged_dname(message.author),
        count=count
    )
    await asyncio.wait([
        client.send_message(message.channel, embed=em),
        client.delete_message(message)
    ])
    return


async def o_servers(client, conn, context, page):
    message = context.message
    em = discord.Embed(colour=0xC5934B)
    em.title = "Top servers"
    pages = int(len(client.servers)/25)+1
    if page > pages:
        return
    em.set_footer(text="Page {} of {}".format(page, pages))
    for i, server in enumerate(sorted(client.servers, key=lambda k: k.member_count, reverse=True), 1):
        if i <= (page-1)*25:
            continue
        em.add_field(
            inline=True,
            name="#{} {}".format(i, server.name),
            value="[{count}](https://{id}.ru \"{id}\")".format(
                count=server.member_count,
                id=server.id
            )
        )
        if i % 25 == 0:
            break
    await asyncio.wait([
        client.delete_message(message),
        client.send_message(message.channel, embed=em)
    ])
    return



# async def o_like(client, conn, context):
#     message = context.message
#     server_id = message.server.id
#     if message.author.bot or message.channel.is_private:
#         return
#     const = await conn.fetchrow("SELECT * FROM settings WHERE discord_id = '{discord_id}'".format(discord_id=server_id))
#     lang = const["locale"]
#     em = discord.Embed(colour=0xC5934B)
#     if not lang in locale.keys():
#         em.description = "{who}, {response}.".format(who=tagged_dname(message.author), response="ошибка локализации")
#         await client.send_message(message.channel, embed=em)
#         return
#     if not const or not const["is_like"]:
#         em.description = locale[lang]["global_not_available"].format(who=tagged_dname(message.author))
#         await client.send_message(message.channel, embed=em)
#         return
#     em = discord.Embed(colour=int(const["em_color"], 16) + 512)
#     try:
#         await client.delete_message(message)
#     except:
#         pass
#     now = int(time.time())
#     if now - const["like_time"] > 14400:
#         likes = const["likes"] + const["like_one"]
#         pop_cached_server(server_id)
#         if likes > 99:
#             likes = 1
#             clear_caches()
#             await conn.execute("UPDATE settings SET likes = DEFAULT, like_time = DEFAULT")
#         await conn.execute("UPDATE settings SET likes = {likes}, like_time = {like_time} WHERE discord_id = '{discord_id}'".format(
#             likes=likes,
#             like_time=now,
#             discord_id=server_id
#         ))
#         global top_servers
#         top_servers = await conn.fetch("SELECT discord_id FROM settings ORDER BY likes DESC, like_time ASC LIMIT 10")
#         em.description = locale[lang]["other_like_success"].format(who=tagged_dname(message.author))
#         em.add_field(
#             name=locale[lang]["other_like_check_it"],
#             value=await u_invite_to_server(client, monitoring_server_id),
#             inline=False
#         )
#     else:
#         t=14400 - now + const["like_time"]
#         h=str(t//3600)
#         m=str((t//60)%60)
#         s=str(t%60)
#         em.description = locale[lang]["other_like_wait"].format(
#             who=tagged_dname(message.author),
#             hours=h,
#             minutes=m,
#             seconds=s
#             )
#         if not server_id in servers_without_follow_us:
#             em = await add_follow_links(client, message, const, em)
#     await client.send_message(message.channel, embed=em)
#     return
#
# async def o_list(client, conn, context, page):
#     message = context.message
#     server_id = message.server.id
#     if message.author.bot or message.channel.is_private:
#         return
#     const = await get_cached_server(conn, server_id)
#     lang = const["locale"]
#     em = discord.Embed(colour=0xC5934B)
#     if not lang in locale.keys():
#         em.description = "{who}, {response}.".format(who=tagged_dname(message.author), response="ошибка локализации")
#         await client.send_message(message.channel, embed=em)
#         return
#     _locale = locale[lang]
#     em = discord.Embed(colour=0x87b5ff)
#     if not const or not const["is_list"]:
#         em.description = _locale["global_not_available"].format(who=tagged_dname(message.author))
#         await client.send_message(message.channel, embed=em)
#         return
#     try:
#         await asyncio.wait([
#             client.delete_message(message),
#             client.send_typing(message.channel)
#         ])
#     except:
#         pass
#     dat = await conn.fetchrow("SELECT COUNT(name) FROM settings WHERE likes > 0")
#     all_count = dat[0]
#     pages = (((all_count - 1) // 10) + 1)
#     if not page:
#         page = 1
#     if page > pages:
#         em.description = _locale["global_page_not_exists"].format(who=tagged_dname(message.author), number=page)
#         await client.send_message(message.channel, embed=em)
#         return
#     em.title = _locale["other_top_of_servers"]
#     if all_count == 0:
#         em.description = _locale["global_list_is_empty"]
#         await client.send_message(message.channel, embed=em)
#         return
#     dat = await conn.fetch("SELECT * FROM settings WHERE likes > 0 ORDER BY likes DESC, like_time DESC LIMIT 10 OFFSET {offset}".format(offset=(page-1)*10))
#     for index, server in enumerate(dat):
#         member_count = 0
#         serv = client.get_server(server["discord_id"])
#         if serv:
#             member_count = serv.member_count
#         if not server["invite"] or not await u_check_invite(client, server["invite"]):
#             link = await u_invite_to_server(client, server["discord_id"])
#             if link:
#                 await conn.execute("UPDATE settings SET invite = '{link}' WHERE discord_id = '{id}'".format(
#                     link=link,
#                     id=server["discord_id"]
#                 ))
#                 pop_cached_server(server["discord_id"])
#             else:
#                 link = "https://discord-server.com/"+server["discord_id"]
#         else:
#             link = server["invite"]
#         em.add_field(
#             name="#{index} {name}".format(
#                 index=(page-1)*10+index+1,
#                 name=server["name"]
#             ),
#             value="<:likes:493040819402702869>\xa0{likes}\xa0\xa0<:users:492827033026560020>\xa0{member_count}\xa0\xa0[<:server:492861835087708162> **__join__**]({link} \"{link_message}\")".format(
#                 likes=server["likes"],
#                 member_count=member_count,
#                 link=link,
#                 link_message=_locale["other_list_link_message"]
#             ),
#             inline=True
#         )
#     em.set_footer(text=_locale["other_footer_page"].format(number=page, length=pages))
#     await client.send_message(message.channel, embed=em)
#     return
#
# async def o_mon(client, conn, context):
#     message = context.message
#     if message.author.bot or message.channel.is_private:
#         return
#     server_id = message.server.id
#     server = message.server
#     const = await get_cached_server(conn, server_id)
#     lang = const["locale"]
#     em = discord.Embed(colour=0xC5934B)
#     if not lang in locale.keys():
#         em.description = "{who}, {response}.".format(who=tagged_dname(message.author), response="ошибка локализации")
#         await client.send_message(message.channel, embed=em)
#         return
#     em = discord.Embed(colour=0x87b5ff)
#     if not const or not const["is_mon"]:
#         em.description = locale[lang]["global_not_available"].format(who=tagged_dname(message.author))
#         await client.send_message(message.channel, embed=em)
#         return
#     em.title = locale[lang]["other_monitoring_tomori"]
#     mon_rank = locale[lang]["other_server_is_not_in_monitoring"]
#     if const["likes"] > 0:
#         mon_rank = await conn.fetchrow("SELECT COUNT(DISTINCT discord_id) AS qty FROM settings WHERE likes > {likes} OR (likes = {likes} AND like_time > {time})".format(likes=const["likes"], time=const["like_time"]))
#         mon_rank = mon_rank[0] + 1
#     em.description = locale[lang]["other_place_in_monitoring"].format(
#         server=server.name,
#         rank=mon_rank
#     )
#     em.add_field(
#         name=locale[lang]["other_like_check_it"],
#         value=await u_invite_to_server(client, monitoring_server_id),
#         inline=False
#     )
#     try:
#         await asyncio.wait([
#             client.delete_message(message),
#             client.send_message(message.channel, embed=em)
#         ])
#     except:
#         pass
#     return

async def o_report(client, conn, context):
    message = context.message
    server_id = message.server.id
    const = await get_cached_server(conn, server_id)
    lang = const["locale"]
    em = discord.Embed(colour=0xC5934B)
    if not lang in locale.keys():
        em.description = "{who}, {response}.".format(who=tagged_dname(message.author), response="ошибка локализации")
        await client.send_message(message.channel, embed=em)
        return
    if not const:
        em.description = locale[lang]["global_not_available"].format(who=tagged_dname(message.author))
        await client.send_message(message.channel, embed=em)
        return
    em = discord.Embed(colour=int(const["em_color"], 16) + 512)
    try:
        await client.delete_message(message)
    except:
        pass
    eD = discord.Embed(color = 0xC5934B, title = "Report from user:", description = message.content)
    eD.add_field(name = "Server", value = "Name: " + message.server.name + "\n" + "Id: `" + message.server.id + "`")
    eD.add_field(name = "Settings", value = "Locale: \"" + const["locale"] + "\"\n" + "Prefix: `" + const["prefix"] + "`")
    eD.add_field(name = "Chat", value = "Name: " + message.channel.name + "\n" + "Id: `" + message.channel.id + "`")
    eD.add_field(name = "User", value = "Name: " + message.author.name + "\n" + "Id: `" + message.author.id + "`\n" + "Display Name: " + message.author.display_name)
    eD.set_author(name = message.author.name, icon_url= message.author.avatar_url)
    await client.send_message(client.get_channel(report_channel_id), embed=eD)

    em.title = locale[lang]["other_report_sent_success"].format(who=tagged_dname(message.author))
    em.set_image(url='https://media.giphy.com/media/xTkcESPybY7bmlKL7O/giphy.gif')
    await client.send_message(message.channel, embed=em)
    return

async def o_ping(client, conn, context):
    message = context.message
    server_id = message.server.id
    const = await get_cached_server(conn, server_id)
    lang = const["locale"]
    em = discord.Embed(colour=0xC5934B)
    if not lang in locale.keys():
        em.description = "{who}, {response}.".format(who=tagged_dname(message.author), response="ошибка локализации")
        await client.send_message(message.channel, embed=em)
        return
    if not const:
        em.description = locale[lang]["global_not_available"].format(who=tagged_dname(message.author))
        await client.send_message(message.channel, embed=em)
        return
    em = discord.Embed(colour=int(const["em_color"], 16) + 512)
    badges = ["verified"]
    _badges = await check_badges(conn, message.author.id, badges)
    if not _badges:
        em.description = locale[lang]["global_have_not_badge"].format(who=tagged_dname(message.author), badge=badges[0])
        await client.send_message(message.channel, embed=em)
        return
    for badge in _badges:
        if not badge in badges:
            em.description = locale[lang]["global_have_not_badge"].format(who=tagged_dname(message.author), badge=badge)
            await client.send_message(message.channel, embed=em)
            return
    try:
        await client.delete_message(message)
    except:
        pass
    now = datetime.utcnow()
    delta = now - message.timestamp
    latency = delta.microseconds / 1000
    em.description=locale[lang]["other_ping"].format(
        who=tagged_dname(message.author),
        latency=int(latency)
        )
    await client.send_message(message.channel, embed=em)
    return

async def o_help(client, conn, context):
    message = context.message
    server_id = message.server.id
    const = await get_cached_server(conn, server_id)
    lang = const["locale"]
    em = discord.Embed(colour=0xC5934B)
    if not lang in locale.keys():
        em.description = "{who}, {response}.".format(who=tagged_dname(message.author), response="ошибка локализации")
        await client.send_message(message.channel, embed=em)
        return
    if not const:
        em.description = locale[lang]["global_not_available"].format(who=tagged_dname(message.author))
        await client.send_message(message.channel, embed=em)
        return
    em = discord.Embed(colour=int(const["em_color"], 16) + 512)
    try:
        await client.delete_message(message)
    except:
        pass
    if message.content.startswith(const["prefix"]+"help ") or message.content.startswith(const["prefix"]+"h "):
        await h_check_help(client, conn, message)
        return
    if not message.content == const["prefix"]+"help" and not message.content == "!help":
        return
    em.title = locale[lang]["other_help_title"]
    em.description = locale[lang]["other_help_desc"].format(const["name"], const["prefix"])
    com_adm = ""
    com_econ = ""
    com_fun = ""
    com_stat = ""
    com_other = ""
    com_mon = ""
    if const["is_say"]:
        com_adm += "``say``, "
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
        com_stat += "``top``, ``money``, "
    if const["is_me"]:
        com_stat += "``me``, "
    com_other = "``help``, "
    if const["is_ping"]:
        com_other += "``ping``, "
    if const["is_avatar"]:
        com_other += "``avatar``, "
    if const["is_report"]:
        com_other += "``report``, "
    if const["is_server"]:
        com_other += "``server``, "
    if const["is_invite"]:
        com_other += "``invite``, "
    if const["is_about"]:
        com_other += "``about``, "
    if const["is_ud"]:
        com_other += "``urban``, "
    com_adm += "``send``, ``start``, ``stop``, ``pay``, "
    if const["is_like"]:
        com_mon += "``like``, "
    if const["is_info"]:
        com_mon += "``info``, "
    if const["is_position"]:
        com_mon += "``position``, "
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
    if not server_id in servers_without_more_info_in_help:
        em.add_field(name=locale[lang]["help_more_info"], value=site_commands_url, inline=False)
    em.set_footer(text=locale[lang]["help_help_by_command"].format(prefix=const["prefix"]))
    await client.send_message(message.channel, embed=em)
    return


async def o_lvlup(client, conn, context, page):
    message = context.message
    server_id = message.server.id
    const = await get_cached_server(conn, server_id)
    lang = const["locale"]
    em = discord.Embed(colour=0xC5934B)
    if not lang in locale.keys():
        em.description = "{who}, {response}.".format(who=tagged_dname(message.author), response="ошибка локализации")
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
    autorole = const["autorole_id"]
    if autorole:
        autorole = discord.utils.get(message.server.roles, id=autorole)
    dat = await conn.fetchrow("SELECT COUNT(condition) FROM mods WHERE type = 'lvlup' AND server_id = '{server_id}'".format(server_id=server_id))
    all_count = dat[0]
    pages = (((all_count - 1) // 24) + 1)
    if not page:
        page = 1
    if all_count == 0 and not autorole:
        em.description = locale[lang]["global_list_is_empty"]
        await client.send_message(message.channel, embed=em)
        return
    if page > pages and not (page == 1 and autorole):
        em.description = locale[lang]["global_page_not_exists"].format(who=tagged_dname(message.author), number=page)
        await client.send_message(message.channel, embed=em)
        return
    if page == 1 and autorole:
        em.add_field(
            name=locale[lang]["other_lvlup_autorole_name"],
            value=autorole.mention,
            inline=True
        )
    dat = await conn.fetch("SELECT * FROM mods WHERE type = 'lvlup' AND server_id = '{server_id}' ORDER BY condition::int ASC LIMIT 24 OFFSET {offset}".format(server_id=server_id, offset=(page-1)*24))
    if dat:
        for index, role in enumerate(dat):
            _role = discord.utils.get(message.server.roles, id=role["value"])
            if _role:
                em.add_field(
                    name="{name} {lvl}".format(lvl=role["condition"], name=locale[lang]["other_lvlup_lvl_name"]),
                    value=_role.mention,
                    inline=True
                )
    else:
        if not autorole:
            em.description = locale[lang]["global_list_is_empty"]
    await client.send_message(message.channel, embed=em)
    return


async def check_lvl_for_sync(client, conn, member, const, roles_data):
    if not const["is_global"]:
        stats_type = member.server.id
    else:
        stats_type = "global"
    dat = await conn.fetchrow("SELECT xp_count FROM users WHERE stats_type = '{stats_type}' AND discord_id = '{discord_id}'".format(stats_type=stats_type, discord_id=member.id))
    if not dat:
        return
    lvl = 0
    i = 1
    if dat["xp_count"] > 0:
        while dat["xp_count"] >= (i * (i + 1) * 5):
            lvl = lvl + 1
            i = i + 1
    lvl = int(lvl/5)*5
    roles = []
    is_new_role = False
    for role in member.roles:
        if not any(role.id==data["value"] for data in roles_data):
            roles.append(role)
    for data in roles_data:
        if not data["condition"] == str(lvl):
            continue
        role = discord.utils.get(member.server.roles, id=data["value"])
        if role and not role in roles:
            is_new_role = True
            roles.append(role)
    if is_new_role:
        try:
            await client.replace_roles(member, *roles)
        except:
            pass

async def o_many(client, conn, context):
    message = context.message
    server_id = message.server.id
    const = await get_cached_server(conn, server_id)
    em = discord.Embed(colour=int(const["em_color"], 16) + 512)
    try:
        await client.delete_message(message)
    except:
        pass
    commands = message.content.split("\n")
    if len(commands) > 1:
        commands.pop(0)
        for command in commands:
            mes = copy.deepcopy(message)
            mes.content = command
            await client.process_commands(mes)
            await asyncio.sleep(1)

async def o_synclvlup(client, conn, context):
    message = context.message
    author = message.author
    server_id = message.server.id
    const = await get_cached_server(conn, server_id)
    em = discord.Embed(colour=int(const["em_color"], 16) + 512)
    try:
        await client.delete_message(message)
    except:
        pass
    roles_data = await conn.fetch("SELECT * FROM mods WHERE server_id = '{server_id}' AND type = 'lvlup'".format(
        server_id=message.server.id
    ))
    if not roles_data:
        await client.send_message(message.channel, "<:users:492827033026560020>")
        return
    for member in message.server.members:
        await check_lvl_for_sync(client, conn, member, const, roles_data)
    await client.send_message(message.channel, "<:kanna:491965559907418112>")


async def o_backgrounds(client, conn, context):
    message = context.message
    server_id = message.server.id
    const = await get_cached_server(conn, server_id)
    lang = const["locale"]
    em = discord.Embed(colour=0xC5934B)
    if not lang in locale.keys():
        em.description = "{who}, {response}.".format(who=tagged_dname(message.author), response="ошибка локализации")
        await client.send_message(message.channel, embed=em)
        return
    if not const:
        em.description = locale[lang]["global_not_available"].format(who=tagged_dname(message.author))
        await client.send_message(message.channel, embed=em)
        return
    em = discord.Embed(colour=int(const["em_color"], 16) + 512)
    try:
        await client.delete_message(message)
    except:
        pass
    if not message.server.id in konoha_servers:
        back_list = random.choice(background_list)
        back_name_list = background_name_list
    else:
        back_list = random.choice(konoha_background_list)
        back_name_list = konoha_background_name_list
    em.title = locale[lang]["other_backgrounds_title"]
    if len(back_list) == 0:
        em.description = locale[lang]["other_backgrounds_list_is_empty"]
        await client.send_message(message.channel, embed=em)
        return
    for i, back in enumerate(back_name_list):
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

    if not const["is_global"]:
        stats_type = server_id
    else:
        stats_type = "global"

async def o_set(client, conn, context, arg1, arg2, args):
    message = context.message
    server_id = message.server.id
    const = await get_cached_server(conn, server_id)
    lang = const["locale"]
    em = discord.Embed(colour=0xC5934B)
    if not lang in locale.keys():
        em.description = "{who}, {response}.".format(who=tagged_dname(message.author), response="ошибка локализации")
        await client.send_message(message.channel, embed=em)
        return
    if not const:
        em.description = locale[lang]["global_not_available"].format(who=tagged_dname(message.author))
        await client.send_message(message.channel, embed=em)
        return
    em = discord.Embed(colour=int(const["em_color"], 16) + 512)
    try:
        await client.delete_message(message)
    except:
        pass


    if arg1 == "badges" or arg1 == "badge":
        if not "staff" in await check_badges(conn, message.author.id, "staff"):
            em = discord.Embed(
                colour=0xC5934B,
                description=locale[lang]["global_have_not_badge"].format(who=tagged_dname(message.author), badge="Staff")
            )
            await asyncio.wait([
                client.delete_message(message),
                client.send_message(message.channel, embed=em)
            ])
            return
        if not arg2:
            em.description = locale[lang]["missed_argument"].format(
                who=tagged_dname(message.author),
                arg="user"
            )
            await client.send_message(message.channel, embed=em)
            return
        if not args:
            em.description = locale[lang]["missed_argument"].format(
                who=tagged_dname(message.author),
                arg="badges"
            )
            await client.send_message(message.channel, embed=em)
            return
        arg2 = clear_name(arg2).lower()
        args = clear_name(args)
        who = discord.utils.get(message.server.members, name=arg2)
        if not who:
            arg2 = re.sub(r'[<@#&!>]+', '', arg2.lower())
            who = discord.utils.get(message.server.members, id=arg2)
        if not who:
            em.description = locale[lang]["incorrect_argument"].format(
                who=tagged_dname(message.author),
                arg="user"
            )
            await client.send_message(message.channel, embed=em)
            return
        await update_badges(conn, who.id, args)
        em.description = "{who}, значки пользователя `{name}` успешно обновлены".format(
            who=tagged_dname(message.author),
            name=who.display_name+"#"+who.discriminator
        )
        await client.send_message(message.channel, embed=em)
        return

    if arg1 in badges_list:
        if not "staff" in await check_badges(conn, message.author.id, "staff"):
            em = discord.Embed(
                colour=0xC5934B,
                description=locale[lang]["global_have_not_badge"].format(who=tagged_dname(message.author), badge="Staff")
            )
            await asyncio.wait([
                client.delete_message(message),
                client.send_message(message.channel, embed=em)
            ])
            return
        if not arg2:
            em.description = locale[lang]["missed_argument"].format(
                who=tagged_dname(message.author),
                arg="user"
            )
            await client.send_message(message.channel, embed=em)
            return
        if not args:
            em.description = locale[lang]["missed_argument"].format(
                who=tagged_dname(message.author),
                arg="badges"
            )
            await client.send_message(message.channel, embed=em)
            return
        arg2 = clear_name(arg2).lower()
        args = clear_name(args)
        who = discord.utils.get(message.server.members, name=arg2)
        if not who:
            arg2 = re.sub(r'[<@#&!>]+', '', arg2.lower())
            who = discord.utils.get(message.server.members, id=arg2)
        if not who:
            em.description = locale[lang]["incorrect_argument"].format(
                who=tagged_dname(message.author),
                arg="user"
            )
            await client.send_message(message.channel, embed=em)
            return
        if not args.isdigit:
            em.description = locale[lang]["incorrect_argument"].format(
                who=tagged_dname(message.author),
                arg="time"
            )
            await client.send_message(message.channel, embed=em)
            return
        dat = await conn.fetchrow("SELECT * FROM mods WHERE type='reset_badge' AND name = '{id}' AND value = '{badge}'".format(id=who.id, badge=arg1))
        if dat:
            await conn.execute("UPDATE mods SET condition = '{time}' WHERE type='reset_badge' AND name = '{id}' AND value = '{badge}'".format(
                time=int(time.time())+int(args),
                id=who.id,
                badge=arg1
            ))
        else:
            await conn.execute("INSERT INTO mods(name, type, condition, value) VALUES('{id}', 'reset_badge', '{time}', '{badge}')".format(
                time=int(time.time())+int(args),
                id=who.id,
                badge=arg1
            ))
        await update_badges(conn, who.id, [arg1])
        t = int(args)
        d = str(t//86400)
        h=str((t%86400)//3600)
        m=str((t//60)%60)
        s=str(t%60)
        em.description = "{who}, Значок **{badge}** для пользователя `{name}` успешно установлен на {d} дней, {h} часов, {m} минут, {s} секунд".format(
            who=tagged_dname(message.author),
            badge=arg1,
            name=who.display_name+"#"+who.discriminator,
            d=d,
            h=h,
            m=m,
            s=s
        )
        await client.send_message(message.channel, embed=em)
        return

    if arg1 == "prefix":
        if not message.author == message.server.owner and not any(role.permissions.administrator for role in message.author.roles):
            em.description = locale[lang]["global_not_allow_to_use"].format(
                who=tagged_dname(message.author)
            )
            await client.send_message(message.channel, embed=em)
            return
        if not arg2:
            em.description = locale[lang]["missed_argument"].format(
                who=tagged_dname(message.author),
                arg="prefix"
            )
            em.description += "\n"+locale[lang]["other_set_prefix_you_can_try"]+" `%s`" % "`, `".join(prefix_list)
            await client.send_message(message.channel, embed=em)
            return
        if arg2 in prefix_list:
            await conn.execute("UPDATE settings SET prefix = '{}' WHERE discord_id = '{}'".format(arg2,server_id))
            pop_cached_server(server_id)
            em.description = locale[lang]["other_set_prefix_success"].format(
                who=tagged_dname(message.author),
                prefix=arg2
            )
            await client.send_message(message.channel, embed=em)
            return
        elif arg2 == "default":
            await conn.execute("UPDATE settings SET prefix = '{}' WHERE discord_id = '{}'".format('!',server_id))
            pop_cached_server(server_id)
            em.description = locale[lang]["other_set_prefix_success"].format(
                who=tagged_dname(message.author),
                prefix='!'
            )
            em.description += "\n" + locale[lang]["other_set_prefix_you_can_try"] + " `%s`" % "`, `".join(prefix_list)
        else:
            em.description = locale[lang]["other_set_prefix_you_can_try"] + " `%s`" % "`, `".join(prefix_list)
        await client.send_message(message.channel, embed=em)
        return

    if arg1 == "gif":
        badges = await check_badges(conn, message.author.id, ["nitro", "staff", "partner"])
        if not ("nitro" in badges or "partner" in badges or "staff" in badges):
            em = discord.Embed(
                colour=0xC5934B,
                description=locale[lang]["global_have_not_badge"].format(who=tagged_dname(message.author), badge="Nitro")
            )
            await asyncio.wait([
                client.delete_message(message),
                client.send_message(message.channel, embed=em)
            ])
            return
        if not arg2:
            # for attach in message.attachments:
            #     # TODO
            em.description = locale[lang]["missed_argument"].format(
                who=tagged_dname(message.author),
                arg="url"
            )
            await client.send_message(message.channel, embed=em)
            return
        arg2 = clear_icon(clear_name(arg2))

        em.description = locale[lang]["other_set_gif_success"].format(
            who=tagged_name(message.author)
        )
        await asyncio.wait([
            client.send_message(message.channel, embed=em),
            conn.execute("UPDATE users SET gif_avatar = '{url}' WHERE discord_id = '{id}' AND stats_type = '{stats_type}'".format(
                url=arg2,
                id=message.author.id,
                stats_type=stats_type
            ))
        ])
        return

    if arg1 == "autorole":
        if not message.author == message.server.owner and not any(role.permissions.administrator for role in message.author.roles):
            em.description = locale[lang]["global_not_allow_to_use"].format(
                who=tagged_dname(message.author)
            )
            await client.send_message(message.channel, embed=em)
            return
        if not arg2:
            em.description = locale[lang]["missed_argument"].format(
                who=tagged_dname(message.author),
                arg="name"
            )
            await client.send_message(message.channel, embed=em)
            return
        if args:
            arg2 = arg2 + " " + args
        role = discord.utils.get(message.server.roles, name=arg2)
        if not role:
            arg2 = re.sub(r'[<@#&!>]+', '', arg2.lower())
            role = discord.utils.get(message.server.roles, id=arg2)
        if not role:
            em.description = locale[lang]["incorrect_argument"].format(
                who=tagged_dname(message.author),
                arg="name"
            )
            await client.send_message(message.channel, embed=em)
            return
        dat = await conn.fetchrow("SELECT prefix FROM settings WHERE discord_id = '{}'".format(message.server.id))
        if dat:
            await conn.execute("UPDATE settings SET autorole_id = '{role_id}' WHERE discord_id = '{server_id}'".format(
                role_id=role.id,
                server_id=message.server.id
            ))
            pop_cached_server(server_id)
        else:
            await conn.execute("INSERT INTO settings(name, discord_id, autorole_id) VALUES('{name}', '{id}', '{role}')".format(
                name=clear_name(message.server.name[:50]),
                id=message.server.id,
                role=role.id
            ))
        em.description = locale[lang]["other_autorole_success_response"].format(
            who=tagged_dname(message.author),
            role_id=role.id
        )
        await client.send_message(message.channel, embed=em)
        return

    if arg1 == "lvlup":
        if not message.author == message.server.owner and not any(role.permissions.administrator for role in message.author.roles):
            em.description = locale[lang]["global_not_allow_to_use"].format(
                who=tagged_dname(message.author)
            )
            await client.send_message(message.channel, embed=em)
            return
        if not arg2:
            em.description = locale[lang]["missed_argument"].format(
                who=tagged_dname(message.author),
                arg="lvl"
            )
            await client.send_message(message.channel, embed=em)
            return
        if not args:
            em.description = locale[lang]["missed_argument"].format(
                who=tagged_dname(message.author),
                arg="role"
            )
            await client.send_message(message.channel, embed=em)
            return
        if not arg2.isdigit():
            em.description = locale[lang]["incorrect_argument"].format(
                who=tagged_dname(message.author),
                arg="lvl"
            )
            await client.send_message(message.channel, embed=em)
            return
        role = discord.utils.get(message.server.roles, name=args)
        if not role:
            args = re.sub(r'[<@#&!>]+', '', args.lower())
            role = discord.utils.get(message.server.roles, id=args)
        if not role:
            em.description = locale[lang]["incorrect_argument"].format(
                who=tagged_dname(message.author),
                arg="role"
            )
            await client.send_message(message.channel, embed=em)
            return
        dat = await conn.fetchrow("SELECT * FROM mods WHERE server_id = '{server}' AND type = 'lvlup' AND condition = '{cond}'".format(
            server=message.server.id,
            cond=arg2
        ))
        if dat:
            await conn.execute("UPDATE mods SET value = '{role}' WHERE server_id = '{server}' AND type = 'lvlup' AND condition = '{cond}'".format(
                role=role.id,
                server=message.server.id,
                cond=dat["condition"]
            ))
        else:
            await conn.execute("INSERT INTO mods(server_id, condition, value, type) VALUES('{server}', '{cond}', '{role}', 'lvlup')".format(
                role=role.id,
                server=message.server.id,
                cond=arg2
            ))
        em.description = locale[lang]["other_lvlup_success_response"].format(
            who=tagged_dname(message.author),
            lvl=arg2,
            role_id=role.id
        )
        await client.send_message(message.channel, embed=em)
        return


    if arg1 == "shop":
        if not message.author == message.server.owner and not any(role.permissions.administrator for role in message.author.roles):
            em.description = locale[lang]["global_not_allow_to_use"].format(
                who=tagged_dname(message.author)
            )
            await client.send_message(message.channel, embed=em)
            return
        if not arg2:
            em.description = locale[lang]["missed_argument"].format(
                who=tagged_dname(message.author),
                arg="name"
            )
            await client.send_message(message.channel, embed=em)
            return
        if not args:
            em.description = locale[lang]["missed_argument"].format(
                who=tagged_dname(message.author),
                arg="cost"
            )
            await client.send_message(message.channel, embed=em)
            return
        args = args.rsplit(" ", 1)
        if len(args) == 2:
            arg2 = arg2 + " " + args[0]
            args = args[1]
            arg2 = arg2.rstrip()
        else:
            args = args[0]
        role = discord.utils.get(message.server.roles, name=arg2)
        if not role:
            arg2 = re.sub(r'[<@#&!>]+', '', arg2.lower())
            role = discord.utils.get(message.server.roles, id=arg2)
        if not role:
            em.description = locale[lang]["incorrect_argument"].format(
                who=tagged_dname(message.author),
                arg="name"
            )
            await client.send_message(message.channel, embed=em)
            return
        if not args.isdigit():
            em.description = locale[lang]["incorrect_argument"].format(
                who=tagged_dname(message.author),
                arg="cost"
            )
            await client.send_message(message.channel, embed=em)
            return
        dat = await conn.fetchrow("SELECT * FROM mods WHERE type = 'shop' AND name = '{name}' AND server_id = '{server_id}'".format(server_id=server_id, name=role.id))
        if dat:
            em.description = locale[lang]["other_set_shop_exists"].format(
                who=tagged_dname(message.author),
                role_id=role.id
            )
        else:
            await conn.execute("INSERT INTO mods(name, server_id, type, condition) VALUES('{name}', '{id}', '{type}', '{cond}')".format(
                name=role.id,
                id=message.server.id,
                type="shop",
                cond=args
            ))
            em.description = locale[lang]["other_shop_success_response"].format(
                who=tagged_dname(message.author),
                role_id=role.id,
                cost=args
            )
        await client.send_message(message.channel, embed=em)
        return



    if arg1 == "language" or arg1 == "lang":
        if not message.author == message.server.owner and not any(role.permissions.administrator for role in message.author.roles):
            em.description = locale[lang]["global_not_allow_to_use"].format(
                who=tagged_dname(message.author)
            )
            await client.send_message(message.channel, embed=em)
            return
        if not arg2:
            em.description = locale[lang]["missed_argument"].format(
                who=tagged_dname(message.author),
                arg="name"
            )
            em.description += "\n" + locale[lang]["other_you_can_try"] + " `%s`" % "`, `".join(short_locales.keys())
            await client.send_message(message.channel, embed=em)
            return
        if args:
            arg2 = arg2 + " " + args
        arg2 = arg2.lower()
        arg2 = short_locales.get(arg2, arg2)
        if not arg2 in locale.keys():
            em.description = locale[lang]["incorrect_argument"].format(
                who=tagged_dname(message.author),
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
            pop_cached_server(server_id)
        else:
            await conn.execute("INSERT INTO settings(name, discord_id, locale) VALUES('{name}', '{id}', '{lang}')".format(
                name=clear_name(message.server.name[:50]),
                id=message.server.id,
                lang=arg2
            ))
        em.description = locale[arg2]["other_lang_success_response"].format(
            who=tagged_dname(message.author),
            lang=arg2
        )
        await client.send_message(message.channel, embed=em)
        return


    if arg1 == "webhook" or arg1 == "wh":
        if not message.author == message.server.owner and not any(role.permissions.administrator for role in message.author.roles):
            em.description = locale[lang]["global_not_allow_to_use"].format(
                who=tagged_dname(message.author)
            )
            await client.send_message(message.channel, embed=em)
            return
        if not arg2:
            em.description = locale[lang]["missed_argument"].format(
                who=tagged_dname(message.author),
                arg="name"
            )
            await client.send_message(message.channel, embed=em)
            return
        if not args:
            em.description = locale[lang]["missed_argument"].format(
                who=tagged_dname(message.author),
                arg="value"
            )
            await client.send_message(message.channel, embed=em)
            return

        arg2 = clear_name(arg2).lower()
        args = clear_name(args)
        if not arg2:
            em.description = locale[lang]["incorrect_argument"].format(
                who=tagged_dname(message.author),
                arg="name"
            )
            await client.send_message(message.channel, embed=em)
            return
        dat = await conn.fetchrow("SELECT * FROM mods WHERE type = 'webhook' AND name = '{name}' AND server_id = '{server_id}'".format(server_id=server_id, name=arg2))
        if dat:
            em.description = locale[lang]["other_set_webhook_exists"].format(
                who=tagged_dname(message.author),
                name=arg2
            )
        else:
            await conn.execute("INSERT INTO mods(name, server_id, type, value) VALUES('{name}', '{id}', '{type}', '{value}')".format(
                name=arg2,
                id=message.server.id,
                type="webhook",
                value=args
            ))
            em.description = locale[lang]["other_webhook_success_response"].format(
                who=tagged_dname(message.author),
                name=arg2
            )
        await client.send_message(message.channel, embed=em)
        return


    if arg1 == "stream":
        if not "nitro" in await check_badges(conn, message.author.id, "nitro"):
            em = discord.Embed(
                colour=0xC5934B,
                description=locale[lang]["global_have_not_badge"].format(who=tagged_dname(message.author), badge="Nitro")
            )
            await asyncio.wait([
                client.delete_message(message),
                client.send_message(message.channel, embed=em)
            ])
            return
        if not message.author == message.server.owner and not any(role.permissions.administrator for role in message.author.roles):
            em.description = locale[lang]["global_not_allow_to_use"].format(
                who=tagged_dname(message.author)
            )
            await client.send_message(message.channel, embed=em)
            return
        if not arg2:
            em.description = locale[lang]["missed_argument"].format(
                who=tagged_dname(message.author),
                arg="user"
            )
            await client.send_message(message.channel, embed=em)
            return
        if not args:
            em.description = locale[lang]["missed_argument"].format(
                who=tagged_dname(message.author),
                arg="text"
            )
            await client.send_message(message.channel, embed=em)
            return

        arg2 = clear_name(arg2).lower()
        args = clear_name(args)
        who = discord.utils.get(message.server.members, name=arg2)
        if not who:
            arg2 = re.sub(r'[<@#&!>]+', '', arg2.lower())
            who = discord.utils.get(message.server.members, id=arg2)
        if not who:
            em.description = locale[lang]["incorrect_argument"].format(
                who=tagged_dname(message.author),
                arg="user"
            )
            await client.send_message(message.channel, embed=em)
            return
        dat = await conn.fetchrow("SELECT * FROM mods WHERE type = 'stream_notification' AND name = '{member}' AND server_id = '{server_id}'".format(server_id=server_id, member=who.id))
        if dat:
            await conn.execute("UPDATE mods SET name='{name}', server_id='{server_id}', type='{type}', condition='{cond}', value='{value}' WHERE id={id}".format(
                name=who.id,
                server_id=message.server.id,
                type="stream_notification",
                cond=message.channel.id,
                value=args,
                id=dat["id"]
            ))
        else:
            await conn.execute("INSERT INTO mods(name, server_id, type, condition, value) VALUES('{name}', '{id}', '{type}', '{cond}', '{value}')".format(
                name=who.id,
                id=message.server.id,
                type="stream_notification",
                cond=message.channel.id,
                value=args
            ))
        em.description = locale[lang]["other_stream_success_response"].format(
            who=tagged_dname(message.author),
            name=who.display_name+"#"+who.discriminator
        )
        await client.send_message(message.channel, embed=em)
        return


    if not arg1:
        em.description = locale[lang]["missed_argument"].format(
            who=tagged_dname(message.author),
            arg="category"
        )
        await client.send_message(message.channel, embed=em)
        return

    em.description = locale[lang]["incorrect_argument"].format(
        who=tagged_dname(message.author),
        arg="category"
    )
    await client.send_message(message.channel, embed=em)
    return



























async def o_remove(client, conn, context, arg1, arg2, args):
    message = context.message
    server_id = message.server.id
    const = await get_cached_server(conn, server_id)
    lang = const["locale"]
    em = discord.Embed(colour=0xC5934B)
    if not lang in locale.keys():
        em.description = "{who}, {response}.".format(who=tagged_dname(message.author), response="ошибка локализации")
        await client.send_message(message.channel, embed=em)
        return
    if not const:
        em.description = locale[lang]["global_not_available"].format(who=tagged_dname(message.author))
        await client.send_message(message.channel, embed=em)
        return
    em = discord.Embed(colour=int(const["em_color"], 16) + 512)
    try:
        await client.delete_message(message)
    except:
        pass


    if arg1 == "autorole":
        if not message.author == message.server.owner and not any(role.permissions.administrator for role in message.author.roles):
            em.description = locale[lang]["global_not_allow_to_use"].format(
                who=tagged_dname(message.author)
            )
            await client.send_message(message.channel, embed=em)
            return
        dat = await conn.execute("UPDATE settings SET autorole_id = NULL WHERE discord_id = '{}'".format(message.server.id))
        pop_cached_server(server_id)
        em.description = locale[lang]["other_autorole_success_delete"].format(
            who=tagged_dname(message.author)
        )
        await client.send_message(message.channel, embed=em)
        return

    if arg1 == "gif":
        badges = await check_badges(conn, message.author.id, ["nitro", "staff", "partner"])
        if not ("nitro" in badges or "partner" in badges or "staff" in badges):
            em = discord.Embed(
                colour=0xC5934B,
                description=locale[lang]["global_have_not_badge"].format(who=tagged_dname(message.author), badge="Nitro")
            )
            await asyncio.wait([
                client.delete_message(message),
                client.send_message(message.channel, embed=em)
            ])
            return

        em.description = locale[lang]["other_remove_gif_success"].format(
            who=tagged_dname(message.author)
        )
        await asyncio.wait([
            client.delete_message(message),
            client.send_message(message.channel, embed=em),
            conn.execute("UPDATE users SET gif_avatar = DEFAULT WHERE discord_id = '{id}' AND stats_type = '{stats_type}'".format(
                id=message.author.id,
                stats_type=stats_type
            ))
        ])
        return

    if arg1 == "lvlup":
        if not message.author == message.server.owner and not any(role.permissions.administrator for role in message.author.roles):
            em.description = locale[lang]["global_not_allow_to_use"].format(
                who=tagged_dname(message.author)
            )
            await client.send_message(message.channel, embed=em)
            return
        if not arg2:
            em.description = locale[lang]["missed_argument"].format(
                who=tagged_dname(message.author),
                arg="lvl"
            )
            await client.send_message(message.channel, embed=em)
            return
        if not arg2.isdigit():
            em.description = locale[lang]["incorrect_argument"].format(
                who=tagged_dname(message.author),
                arg="lvl"
            )
            await client.send_message(message.channel, embed=em)
            return
        dat = await conn.fetchrow("SELECT * FROM mods WHERE type = 'lvlup' AND condition = '{lvl}' AND server_id = '{server_id}'".format(server_id=server_id, lvl=arg2))
        if not dat:
            em.description = locale[lang]["other_lvlup_not_exists"].format(
                who=tagged_dname(message.author),
                lvl=arg2
            )
        else:
            await conn.execute("DELETE FROM mods WHERE type = 'lvlup' AND condition = '{lvl}' AND server_id = '{server_id}'".format(server_id=server_id, lvl=arg2))
            em.description = locale[lang]["other_lvlup_success_delete"].format(
                who=tagged_dname(message.author),
                role_id=dat["value"],
                lvl=arg2
            )
        await client.send_message(message.channel, embed=em)
        return


    if arg1 == "badges" or arg1 == "badge":
        if not "staff" in await check_badges(conn, message.author.id, "staff"):
            em = discord.Embed(
                colour=0xC5934B,
                description=locale[lang]["global_have_not_badge"].format(who=tagged_dname(message.author), badge="Staff")
            )
            await asyncio.wait([
                client.delete_message(message),
                client.send_message(message.channel, embed=em)
            ])
            return
        if not arg2:
            em.description = locale[lang]["missed_argument"].format(
                who=tagged_dname(message.author),
                arg="user"
            )
            await client.send_message(message.channel, embed=em)
            return
        arg2 = clear_name(arg2).lower()
        who = discord.utils.get(message.server.members, name=arg2)
        if not who:
            arg2 = re.sub(r'[<@#&!>]+', '', arg2.lower())
            who = discord.utils.get(message.server.members, id=arg2)
        if not who:
            em.description = locale[lang]["incorrect_argument"].format(
                who=tagged_dname(message.author),
                arg="user"
            )
            await client.send_message(message.channel, embed=em)
            return
        if not args:
            await conn.execute("DELETE FROM mods WHERE type = 'badges' AND name = '{name}'".format(name=who.id))
            em.description = "{who}, значки пользователя `{name}` успешно удалены".format(
                who=tagged_dname(message.author),
                name=who.display_name+"#"+who.discriminator
            )
            await client.send_message(message.channel, embed=em)
            return
        args = clear_name(args).lower()

        dat = await conn.fetchrow("SELECT * FROM mods WHERE type = 'badges' AND name = '{member}'".format(member=who.id))
        if dat:
            badges = []
            for badge in dat["arguments"]:
                if badge in badges_list and not badge in args:
                    badges.append(badge)
            if badges:
                await conn.execute("UPDATE mods SET arguments=ARRAY['{args}'] WHERE type = 'badges' AND name='{name}'".format(
                    name=who.id,
                    args="', '".join(badges)
                ))
                em.description = "{who}, значки пользователя `{name}` успешно обновлены".format(
                    who=tagged_dname(message.author),
                    name=who.display_name+"#"+who.discriminator
                )
            else:
                await conn.execute("DELETE FROM mods WHERE type = 'badges' AND name = '{name}'".format(name=who.id))
                em.description = "{who}, значки пользователя `{name}` удалены".format(
                    who=tagged_dname(message.author),
                    name=who.display_name+"#"+who.discriminator
                )
        else:
            em.description = "{who}, у пользователя `{name}` нет значков".format(
                who=tagged_dname(message.author),
                name=who.display_name+"#"+who.discriminator
            )
        await client.send_message(message.channel, embed=em)
        return

    if arg1 == "webhook" or arg1 == "wh":
        if not message.author == message.server.owner and not any(role.permissions.administrator for role in message.author.roles):
            em.description = locale[lang]["global_not_allow_to_use"].format(
                who=tagged_dname(message.author)
            )
            await client.send_message(message.channel, embed=em)
            return
        if not arg2:
            em.description = locale[lang]["missed_argument"].format(
                who=tagged_dname(message.author),
                arg="name"
            )
            await client.send_message(message.channel, embed=em)
            return

        arg2 = clear_name(arg2).lower()
        if not arg2:
            em.description = locale[lang]["incorrect_argument"].format(
                who=tagged_dname(message.author),
                arg="name"
            )
            await client.send_message(message.channel, embed=em)
            return
        dat = await conn.fetchrow("SELECT * FROM mods WHERE type = 'webhook' AND name = '{name}' AND server_id = '{server_id}'".format(server_id=server_id, name=arg2))
        if not dat:
            em.description = locale[lang]["other_webhook_not_exists"].format(
                who=tagged_dname(message.author),
                name=arg2
            )
        else:
            await conn.execute("DELETE FROM mods WHERE type = 'webhook' AND name = '{name}' AND server_id = '{server_id}'".format(server_id=server_id, name=arg2))
            em.description = locale[lang]["other_webhook_success_delete"].format(
                who=tagged_dname(message.author),
                name=arg2
            )
        await client.send_message(message.channel, embed=em)
        return


    if arg1 == "stream":
        if not "nitro" in await check_badges(conn, message.author.id, "nitro"):
            em = discord.Embed(
                colour=0xC5934B,
                description=locale[lang]["global_have_not_badge"].format(who=tagged_dname(message.author), badge="Nitro")
            )
            await asyncio.wait([
                client.delete_message(message),
                client.send_message(message.channel, embed=em)
            ])
            return
        if not message.author == message.server.owner and not any(role.permissions.administrator for role in message.author.roles):
            em.description = locale[lang]["global_not_allow_to_use"].format(
                who=tagged_dname(message.author)
            )
            await client.send_message(message.channel, embed=em)
            return
        if not arg2:
            em.description = locale[lang]["missed_argument"].format(
                who=tagged_dname(message.author),
                arg="user"
            )
            await client.send_message(message.channel, embed=em)
            return

        arg2 = clear_name(arg2).lower()
        who = discord.utils.get(message.server.members, name=arg2)
        if not who:
            arg2 = re.sub(r'[<@#&!>]+', '', arg2.lower())
            who = discord.utils.get(message.server.members, id=arg2)
        if not who:
            em.description = locale[lang]["incorrect_argument"].format(
                who=tagged_dname(message.author),
                arg="user"
            )
            await client.send_message(message.channel, embed=em)
            return
        await conn.execute("DELETE FROM mods WHERE type = 'stream_notification' AND name = '{member}' AND server_id = '{server_id}'".format(server_id=server_id, member=who.id))
        em.description = locale[lang]["other_stream_success_delete"].format(
            who=tagged_dname(message.author),
            name=who.display_name+"#"+who.discriminator
        )
        await client.send_message(message.channel, embed=em)
        return


    if arg1 == "shop":
        if not message.author == message.server.owner and not any(role.permissions.administrator for role in message.author.roles):
            em.description = locale[lang]["global_not_allow_to_use"].format(
                who=tagged_dname(message.author)
            )
            await client.send_message(message.channel, embed=em)
            return
        if not arg2:
            em.description = locale[lang]["missed_argument"].format(
                who=tagged_dname(message.author),
                arg="name"
            )
            await client.send_message(message.channel, embed=em)
            return
        if args:
            arg2 = arg2 + " " + args
        logg.info("remove arg2 = {arg2}".format(arg2=arg2))
        role = discord.utils.get(message.server.roles, name=arg2)
        if not role:
            arg2 = re.sub(r'[<@#&!>]+', '', arg2.lower())
            role = discord.utils.get(message.server.roles, id=arg2)
        if not role:
            em.description = locale[lang]["incorrect_argument"].format(
                who=tagged_dname(message.author),
                arg="name"
            )
            await client.send_message(message.channel, embed=em)
            return
        dat = await conn.fetchrow("SELECT * FROM mods WHERE type = 'shop' AND name = '{name}' AND server_id = '{server_id}'".format(server_id=server_id, name=role.id))
        if not dat:
            em.description = locale[lang]["other_shop_not_exists"].format(
                who=tagged_dname(message.author),
                role_id=role.id
            )
        else:
            await conn.execute("DELETE FROM mods WHERE type = 'shop' AND name = '{name}' AND server_id = '{server_id}'".format(server_id=server_id, name=role.id))
            em.description = locale[lang]["other_shop_success_delete"].format(
                who=tagged_dname(message.author),
                role_id=role.id
            )
        await client.send_message(message.channel, embed=em)
        return


    if not arg1:
        em.description = locale[lang]["missed_argument"].format(
            who=tagged_dname(message.author),
            arg="category"
        )
        await client.send_message(message.channel, embed=em)
        return

    em.description = locale[lang]["incorrect_argument"].format(
        who=tagged_dname(message.author),
        arg="category"
    )
    await client.send_message(message.channel, embed=em)
    return
