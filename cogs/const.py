import discord
import asyncio
import re
import logging
import json
import random
from PIL import Image, ImageChops, ImageFont, ImageDraw, ImageSequence, ImageFilter
from PIL.GifImagePlugin import getheader, getdata
from functools import partial
import aiohttp
from io import BytesIO
from typing import Union
from aiohttp import ClientSession
from cogs.discord_hooks import Webhook
from config.settings import settings
from config.constants import *



HEADERS = {
    'authorization': "Bot "+settings["token"],
    'user-agent': "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) discord/0.0.305 Chrome/69.0.3497.128 Electron/4.0.8 Safari/537.36",
    'Content-Type': 'application/json'
}


async def get_webhooks(client, **kwargs):
    server = kwargs.get("server")
    channel = kwargs.get("channel")

    url = None
    if server:
        url = "https://discordapp.com/api/v6/guilds/{guild.id}/webhooks".format(guild=server)
    elif channel:
        url = "https://discordapp.com/api/v6/channels/{channel}/webhooks".format(channel=channel)

    if url:
        async with ClientSession() as session:
            async with session.get(url, headers=HEADERS) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return None

async def create_webhook(client, **kwargs):
    payload = {
        # "avatar": kwargs.get("avatar"), # TODO
        "name": kwargs.get("name", "No Name")
    }
    channel = kwargs.get("channel")

    url = "https://discordapp.com/api/v6/channels/{channel}/webhooks".format(channel=channel)

    async with ClientSession() as session:
        async with session.post(url, data=json.dumps(payload), headers=HEADERS) as response:
            if response.status == 200:
                return await response.json()
            else:
                return None


async def send_webhook(message, **kwargs):
    client = kwargs.get("client")
    assert client, "Command send_webhook: Can't load client object"
    assert message, "Command send_webhook: Can't load message object"

    webhooks = await get_webhooks(client, channel=message.channel.id)
    if not webhooks:
        webhooks = []
        webhooks.append(await create_webhook(client, name="Tomori Nitro Webhook", channel=message.channel.id))

    # assert len(webhooks) > 0, "Command send_webhook: Can't create webhook on channel {}".format(message.channel.id)
    if len(webhooks) < 1:
        await client.send_message(message.channel, "I can't create webhook on that channel")
        return False

    wh_url = "https://discordapp.com/api/v6/webhooks/{id}/{token}".format(
        id=webhooks[0].get("id"),
        token=webhooks[0].get("token")
    )

    content = kwargs.get("content")
    embed = kwargs.get("embed", {})
    file = kwargs.get("file")

    args = {}
    args["text"] = content
    args["file"] = file
    for key, value in embed.items():
        args[key] = value

    args["username"] = message.author.display_name
    args["avatar_url"] = message.author.avatar_url.rsplit(".", maxsplit=1)[0]+".png"

    msg = Webhook(web_url=wh_url, **args)
    await msg.post()


async def just_send_webhook(wh_url, **kwargs):
    content = kwargs.get("content")
    embed = kwargs.get("embed", {})
    file = kwargs.get("file")

    args = {}
    args["text"] = content
    args["file"] = file
    for key, value in embed.items():
        args[key] = value

    args["username"] = kwargs.get("username")
    args["avatar_url"] = kwargs.get("avatar_url")

    msg = Webhook(web_url=wh_url, **args)
    await msg.post()


async def true_send_message(s_info, client, message, content=None, embed=discord.Embed.Empty, file=None):
    if not message:
        return
    if s_info["webhook_icon"] or s_info["webhook_name"]:
        await send_webhook(message, client=client, content=content, embed=embed, files=files)
    else:
        try:
            await client.send_message(message.channel, content=content, embed=embed)
        except discord.Forbidden:
            try:
                em = discord.Embed(colour=0xFAD6A5)
                em.title = "🚫 Error"
                em.description = "I can't send a message to channel "+str(message.channel.mention)
                await client.send_message(message.author, embed=em)
            except:
                pass
        except discord.HTTPException:
            pass


def tagged_name(user):
    return "{0.name}#{0.discriminator}".format(user)

def tagged_name_id(user):
    return "{0.name}#{0.discriminator} [{0.id}]".format(user)

def tagged_dname(user):
    return "{0.display_name}#{0.discriminator}".format(user)


def beauty_icon(url, default="webp"):
    urls = url.rsplit(".", maxsplit=1)
    code = urls[0]
    code = code.rsplit("/", maxsplit=1)
    if code[1].startswith("a_"):
        return code[0]+"/"+code[1]+".gif"
    if not default:
        return code[0]+"/"+code[1] + "." + urls[1].split("/", maxsplit=1)[0].split("?", maxsplit=1)[0]
    return code[0] + "/" + code[1] + "." + str(default)

def clear_icon(url):
    try:
        code = url.rsplit(".", maxsplit=1)
        code = code[0] + "." + code[1].split("/", maxsplit=1)[0].split("?", maxsplit=1)[0]
        return code
    except:
        return None





rainbow_roles = {
    # West Wild
    '458947364137467906': '535771100412379138'
}
rainbow_colors = [
    0xFF0000,
    0xFF4500,
    0xFFFF00,
    0x00FF00,
    0x00FFFF,
    0x0000FF,
    0x8A2BE2,
    0x000000,
    0xBC8F8F,
    0xFF00FF,
    0xA52A2A,
    0x9ACD32
]



not_all_channels_work = {
# 美波 (Minami) Fan Zone
"549251000167301120":[
    "549265213069721638",
    "550000414263738369",
    "550000437349318666"
],
# Neko.land
"525360269023641631":[
    "525360773216600104",
    "525360774613565460"
],
# West Wild
"458947364137467906":[]
}


moon_server = {
"злиться":{
    "response":"{author} злиться на {user}. Хм... что же он(а) такого сделал(а)?",
    "is_who": "True",
    "gifs":[
        "https://cdn.discordapp.com/attachments/504948339809320960/506771700759658516/baka2.gif",
        "https://cdn.discordapp.com/attachments/504948339809320960/506771698864095262/baka1.gif",
        "https://cdn.discordapp.com/attachments/504948339809320960/515534398515314702/12.gif",
        "https://cdn.discordapp.com/attachments/504948339809320960/515534394719469588/11.gif",
        "https://cdn.discordapp.com/attachments/504948339809320960/515534362700283919/10.gif",
        "https://cdn.discordapp.com/attachments/504948339809320960/515534356761149440/9.gif",
        "https://cdn.discordapp.com/attachments/504948339809320960/515534355444137985/8.gif",
        "https://cdn.discordapp.com/attachments/504948339809320960/515534330886619138/7.gif",
        "https://cdn.discordapp.com/attachments/504948339809320960/515534315262836746/6.gif",
        "https://cdn.discordapp.com/attachments/504948339809320960/515534300007890945/5.gif",
        "https://cdn.discordapp.com/attachments/504948339809320960/515534289815863306/4.gif",
        "https://cdn.discordapp.com/attachments/504948339809320960/515534276398284804/3.gif",
        "https://cdn.discordapp.com/attachments/504948339809320960/515534260472512533/2.gif",
        "https://cdn.discordapp.com/attachments/504948339809320960/515534256995434546/1.gif",
        "https://cdn.discordapp.com/attachments/504948339809320960/515534249399549953/13.gif",
        "https://cdn.discordapp.com/attachments/504948339809320960/506771703129440256/baka3.gif"
    ]
},
"поцеловать":{
    "response":"Оу... {author} миленько поцеловал {user}. Этим котикам явно нужно быть вместе!",
    "is_who": "True",
    "gifs":[
        "https://cdn.discordapp.com/attachments/504948339809320960/515536956520792075/11.gif",
        "https://cdn.discordapp.com/attachments/504948339809320960/515536938837737472/10.gif",
        "https://cdn.discordapp.com/attachments/504948339809320960/515536933384880128/9.gif",
        "https://cdn.discordapp.com/attachments/504948339809320960/515536920621875200/8.gif",
        "https://cdn.discordapp.com/attachments/504948339809320960/515536909712228367/7.gif",
        "https://cdn.discordapp.com/attachments/504948339809320960/515536896286392340/6.gif",
        "https://cdn.discordapp.com/attachments/504948339809320960/515536885217493032/5.gif",
        "https://cdn.discordapp.com/attachments/504948339809320960/515536867131654149/4.gif",
        "https://cdn.discordapp.com/attachments/504948339809320960/515536852405452800/3.gif",
        "https://cdn.discordapp.com/attachments/504948339809320960/515536838736347146/2.gif",
        "https://cdn.discordapp.com/attachments/504948339809320960/515536814035959828/1.gif",
        "https://cdn.discordapp.com/attachments/504948339809320960/515536791311220736/12.gif"
    ]
},
"грустить":{
    "response":"Милый котик {author} грустит...",
    "gifs":[
        "https://cdn.discordapp.com/attachments/504948339809320960/506772539507212288/sad1.gif",
        "https://cdn.discordapp.com/attachments/504948339809320960/506772544414547968/sad2.gif",
        "https://cdn.discordapp.com/attachments/504948339809320960/506772566032121858/sad4.gif",
        "https://cdn.discordapp.com/attachments/504948339809320960/506772577834762250/sad5.gif",
        "https://cdn.discordapp.com/attachments/504948339809320960/506772582272335882/sad6.gif",
        "https://cdn.discordapp.com/attachments/504948339809320960/506772597401321472/sad7.gif",
        "https://cdn.discordapp.com/attachments/504948339809320960/506773144237768714/tumblr_ou87z3uTEv1wuhq9yo1_500.gif",
        "https://cdn.discordapp.com/attachments/510795545791430656/515533997137461279/9cef9ac83a77994a.gif",
        "https://cdn.discordapp.com/attachments/510795545791430656/515534034592595968/1.gif",
        "https://cdn.discordapp.com/attachments/510795545791430656/515534046965661726/2.gif",
        "https://cdn.discordapp.com/attachments/539086777542246400/554643486230446091/3d43c39cfad283c3-sad-animated-gif-2-anime-cry-eyes-game-gif-bio-my.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/554643529792487434/3f1b014c410df4d7ecb19439df1e9356fec72f9ar1-392-288_hq.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/554643579533000715/45a.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/554643627658182671/62H1.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/554643666992496650/1541595758_8d6f437c76dd1c9919241eaa9163f29c.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/554643705647333376/68747470733a2f2f6d656469612e67697068792e636f6d2f6d656469612f31346263344c7a51434c377370612f736f757263.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/554643756834488330/68747470733a2f2f73332e616d617a6f6e6177732e636f6d2f776174747061642d6d656469612d736572766963652f53746f.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/554643797359853578/203396775003202.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/554643835393933327/animated-sad-image-0019.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/554643883305205760/Anime-Gif-with-Sad-Face-3.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/554643921808916491/BasicHarmfulAlligatorsnappingturtle-small.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/554643964620439552/BQM6jEZ-UJLgGUuvrNkYUCG8p-X1WhZLiR4h-oxkqQdqHrJHiKZ4KaGQOmlUpp95VkOtHSiFmpA9dELbOu_ZUw.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/554644008375287808/Ete3.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/554644061663920158/G0tZ.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/554644099718971392/image_862103180032309586413.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/554644141531987968/orig.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/554644187413217280/pezOkg9.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/554644228039245837/Sad-Azusa-GIF-nakano-azusa-34132120-500-273.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/554644276038991882/sad-cute-anime-gif-7.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/554645666081669130/t1enor_2.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/554645705076244483/tenor_2.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/554645771740512256/tenor_11.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/554645872076652544/tenor_31.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/554645918574575616/tenor_111.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/554645975608721418/tenor.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/554646013378560003/tumblr_mvh32tGYfz1qbvovho1_500.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/554646051718430736/tumblr_no3807STUd1thlt5lo1_500.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/554646095850897424/tumblr_o5qo3tcksc1vnbupao1_540.gif",
        "https://cdn.discordapp.com/attachments/510795545791430656/515534054574260284/3.gif"
    ]
},
"секс":{
    "response":"{author} Хочет заняться сексом с {user}. Сейчас будет жарко",
    "is_who": "True",
    "gifs":[
        "https://cdn.discordapp.com/attachments/504948339809320960/506773551991488522/sex1.gif",
        "https://cdn.discordapp.com/attachments/504948339809320960/506773548870926337/sex_1.gif",
        "https://cdn.discordapp.com/attachments/504948339809320960/506773562288504833/sex2.gif",
        "https://cdn.discordapp.com/attachments/504948339809320960/506773569892646912/sex3.gif",
        "https://cdn.discordapp.com/attachments/504948339809320960/506773575135657984/sex4.gif",
        "https://cdn.discordapp.com/attachments/504948339809320960/506773585491394570/sex6.gif",
        "https://cdn.discordapp.com/attachments/504948339809320960/506773594529857537/sex7.gif",
        "https://cdn.discordapp.com/attachments/504948339809320960/506773599877726215/sex8.gif",
        "https://cdn.discordapp.com/attachments/504948339809320960/515536637485121547/d16b66732e3a53a7.gif"
    ]
},
"суицид":{
    "response":"{author} ушёл(a) в мир иной... прощай, мы будем скучать",
    "gifs":[
        "https://cdn.discordapp.com/attachments/504948339809320960/506774310107611136/suicide1.gif",
        "https://cdn.discordapp.com/attachments/504948339809320960/506774311743520776/suicide2.gif",
        "https://cdn.discordapp.com/attachments/510795545791430656/515534006981361675/suicide_1.gif",
        "https://cdn.discordapp.com/attachments/510795545791430656/515534016901021706/suicide_2.gif",
        "https://cdn.discordapp.com/attachments/539086777542246400/555416474366509097/18-20-44-c7da2125d2bcc8be291c2faaa78c5274e0ccf7a9_hq.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/555416504708104212/18-21-20-tumblr_lquyvrAPMU1qbajlmo1_r4_500.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/555416541953261568/18-22-40-286479511117x630.gif",
        "https://cdn.discordapp.com/attachments/510795545791430656/515534030335115264/suicide_3.gif"
    ]
},
"гладить":{
    "response":"{author} гладит {user}. Это так мило ^^",
    "is_who": "True",
    "gifs":[
        "https://cdn.discordapp.com/attachments/504948339809320960/506774656842465300/1.gif",
        "https://cdn.discordapp.com/attachments/504948339809320960/506774662957498389/3.gif",
        "https://cdn.discordapp.com/attachments/504948339809320960/506774662231883787/2.gif",
        "https://cdn.discordapp.com/attachments/504948339809320960/506774668913541135/5.gif",
        "https://cdn.discordapp.com/attachments/504948339809320960/506775581271261184/4.gif"
    ]
},
"смущаюсь":{
    "response":"{author} ooow, Меня засмущали :с",
    "gifs":[
        "https://cdn.discordapp.com/attachments/504948339809320960/506775708492890112/3.gif",
        "https://cdn.discordapp.com/attachments/504948339809320960/506775700842348544/2.gif",
        "https://cdn.discordapp.com/attachments/539086777542246400/555414500266999823/0ab2d4f29dFXXWNCT_145401_5f76a92c60.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/555414549386362890/1483612841_59.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/555414585474023455/15462557425700.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/555414620404187196/AEvw.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/555414664607957003/anime-girl-gif-smile-6.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/555414698238148608/CE3V.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/555414733751058453/chiyo-sakura-gif-14.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/555414765007011890/comment_ghBADHw4WsnpEa4nMDJIgkMNlhZLvXzy.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/555414800285302785/comment_WGZAW2DqxTbRptYfi8mjN5mkqFzIDlZz.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/555414835030917121/f975bdb1f9ec57621440825425deafd18733d2417cb8f7e0ef4f4c74c78845bb.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/555414864873521153/giphy_1.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/555414893696778250/giphy.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/555414931927728128/QHqW.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/555414961887903754/sakura-chiyo-gif-14.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/555414998663430154/tenor_1.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/555415059363528714/YPLH.gif",
        "https://cdn.discordapp.com/attachments/504948339809320960/506775695263924224/1.gif"
    ]
},
"кусь":{
    "response":"Кусь! {author} укусил(a) {user}",
    "is_who": "True",
    "gifs":[
        "https://cdn.discordapp.com/attachments/504948339809320960/506776383175786506/2.gif",
        "https://cdn.discordapp.com/attachments/504948339809320960/506776387022225408/1.gif",
        "https://cdn.discordapp.com/attachments/504948339809320960/506776393162686465/3.gif",
        "https://cdn.discordapp.com/attachments/504948339809320960/515536166767034377/1.gif",
        "https://cdn.discordapp.com/attachments/504948339809320960/515536168121663508/3.gif",
        "https://cdn.discordapp.com/attachments/504948339809320960/515536178359828480/2.gif",
        "https://cdn.discordapp.com/attachments/504948339809320960/506776398489190400/4.gif"
    ]
},
"обнять":{
    "response":"{author} обнял(а) {user}. Это так романтично",
    "is_who": "True",
    "gifs":[
        "https://cdn.discordapp.com/attachments/504948339809320960/506777002309582863/1.gif",
        "https://cdn.discordapp.com/attachments/504948339809320960/506777067539398656/1.gif",
        "https://cdn.discordapp.com/attachments/504948339809320960/506777070899298316/2.gif",
        "https://cdn.discordapp.com/attachments/504948339809320960/506777079975510016/3.gif",
        "https://cdn.discordapp.com/attachments/504948339809320960/515536388788060162/3.gif",
        "https://cdn.discordapp.com/attachments/504948339809320960/515536400439967794/4.gif",
        "https://cdn.discordapp.com/attachments/504948339809320960/515536417170915329/5.gif",
        "https://cdn.discordapp.com/attachments/504948339809320960/506777090629304340/4.gif"
    ]
},

"meme":{
    "response":"",
    "gifs":[
"https://cdn.discordapp.com/attachments/539086777542246400/554637691174649857/1adc959cb0f2787fcb9faac08bcc19f0.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/554639224620711947/6d9265d2f0e3fd51d6e742bc2c910dd6.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/554639413834022919/8c2d68da73ae863ff053694e219e2c5e71ba6902_hq.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/554639509661155328/58b.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/554639612950216704/171.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/554639677500424203/1807c4b782dc0ee5ab6093cc05bc3c5e1226728718_full.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/554639763362283530/8652a311d374ac0199e2e8ca46c674ebf25749d8_00.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/554639837496475649/70913.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/554639905809104896/1721476.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/554639983533883392/1463798114_Ritsu4.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/554640062575280136/AFLM.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/554640127893438485/anigif_sub-buzz-4673-1522954232-8.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/554640202157654019/Anime_8426f6_6242123.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/554640356403183636/anime-gif-graciosos-8.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/554640589337919498/be643fd4e5fa8e4994c0232cf837d50c.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/554640660926300160/e63.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/554640721177608192/g4rxtC6fNRjry.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/554640809513844765/giphy.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/554640877927006213/image.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/554640949364523008/IzUOPuB.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/554641016792154162/magspace.ru_88888888888888888888888888888888.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/554641113080659978/meme5.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/554641167392964608/o1riginal.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/554641224414265345/original.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/554641300213858314/plz9VSb.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/554641361811275796/Pve.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/554641403557445634/tenor_1.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/554641457303257098/tenor_2.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/554641507165011998/tenor.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/554641682088591373/tumblr_m2df2z5XuW1qi87mmo1_r3_500.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/554641755593637888/X3ln.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/554641806315487243/1.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/554641846014574595/3e576241cf297adb.gif"
    ]
},

"бой":{
    "response":"Я {author} вызываю тебя на поединок {user}! Спорим я тебя сломаю на мелкие кусочки?!",
    "is_who": "True",
    "gifs":[
"https://cdn.discordapp.com/attachments/539086777542246400/554642096909451264/1VWI.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/554642141549297664/3Ll0.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/554642231005282344/5Mxb.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/554642266610728966/8Ikg.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/554642304271646738/9uqS.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/554642343194656769/40RA.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/554642397984849930/51d27f60a216462ddfe0ddda4551bf8d.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/554642660707794994/79pT.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/554642719197233162/841d4f2bcd756dc8246bcbebf0f08430ac09e2b1_hq.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/554642769382211584/1411817478_1218677180.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/554642814080778261/1481078943-5cbbacb81272788f89921e868c6322e5.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/554642855566639105/1512046595_rt.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/554642909685612564/AUaY.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/554642967155965972/BBPEAccel.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/554643007660621865/c89c194179b2023796055e69f9b7fd2d.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/554643072819003412/giphy.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/554643263420760083/Tumblr_naikxjkyiU1r2yf1qo5_500.gif"
    ]
},

"утро":{
    "response":"Хей! Вы только посмотрите кто проснулся {author}! Доброе утро, солнышко <:",
    "gifs":[
"https://cdn.discordapp.com/attachments/539086777542246400/555416598199009280/6cb27b77fd8247904d82ac9acef98c75ce414db0_hq.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/555416627274055691/7KjH.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/555416658475220993/9b16dd4ebc2625bd24f9a973927e640f8a6e6c2a_hq.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/555416706558984203/41db3e5b78c5d85509659d3d11a519700fed7606r1-500-500_hq.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/555416744215183381/396.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/555416776419049482/1093ad4d675617b274c284c62da58f3b.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/555416807129874472/3733948e8dc402b537d78d6e523840918661992f_hq.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/555416848816930816/1446101065_tumblr_nwepdpRakx1qg78wpo1_500.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/555416890789593098/1443128246888.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/555416929007829022/BossyExcitableAmurminnow-size_restricted.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/555416963241738250/d5d17a968db14cc73074bd92a3c1d10505df225c_hq.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/555417078450880513/e7820a120fc491e6ef99eb82c33b768d.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/555417112613617664/haastetumblr_mmrshedhyr1s5r7rso1_500.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/555417148101623828/K5fmlck.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/555417195530682369/large.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/555417229311737858/morning-anime-gif-7.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/555417268771749889/original_2.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/555417443137486868/tenor_2.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/555417570782740480/tumblr_mfymmal6gd1rosuzvo1_500.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/555417606056706058/tumblr_msdd8ae7OC1r2pvg2o1_500.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/555417639518732298/tumblr_msebj3dNj11sq9yswo1_500.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/555417673165438997/xwNFjbgF_b13g2rn4OUgk7UuaLuC38qqjAUWBJ1QzIdSTCCsk-kdbznDlxdrvHhOhmDZbTt_YLFVx6zuHQXRvMCW9N-o4mssab5R.gif"
    ]
},

"кушац":{
    "response":"{author} ням, нямка! Можно ещё еды? :З",
    "gifs":[
"https://cdn.discordapp.com/attachments/539086777542246400/554654693482299395/2.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/554654740072497172/4bf4195a667e6f974b9df888a9879952a69d10f5_hq.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/554654777447809054/9bQH.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/554654819852353537/49320ef3dc2730a8ac89c1e5a7fba3608ff02958_hq.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/554654875686928384/191896190002202.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/554654916149510175/c24.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/554655398615842833/eating-anime-gif-9.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/554655440810541056/giphy.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/554655474398789632/MajorEverlastingBudgie-size_restricted.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/554655515897102337/orig.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/554655559295696896/original.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/554655686722715668/tenor_1.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/554655726631387136/tenor_2.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/554655766192062475/tenor.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/554655804729327636/tumblr_n1rc5rjxov1ts7hx5o1_500.gif"
    ]
},

"рад":{
    "response":"Йухууу! У {author} хорошое настроение! Тьмок его :з",
    "gifs":[
"https://cdn.discordapp.com/attachments/539086777542246400/555413488072392714/15ff213fbc996fb03345991c927108b55a75f66f_hq.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/555413522507497492/63ca58fb23c0901176abf1787fa3bfce.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/555413554874810383/873.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/555413592430739456/1478928084_Tumblr_m5l36smcQo1ryw2xmo1_1280.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/555413623170924544/191956697002202.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/555413647967518740/AnxiousShimmeringAmericanriverotter-size_restricted.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/555413683040157708/b3d516636dcb886d3606a0ad88f86ffd.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/555413711045787649/CapitalSereneAlbertosaurus-max-1mb.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/555413747619856384/CleanSecondhandAlpineroadguidetigerbeetle-small.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/555413780935213106/f975bdb1f9ec57621440825425deafd18733d2417cb8f7e0ef4f4c74c78845bb.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/555413814032465931/fa2349f30bbf9d259dc313d5a4021d89.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/555413854444847104/fcd0075d3b9fe305faa182b42c462c03f51fbcd2_00.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/555413890503147530/giphy_1.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/555413938917867530/giphy_2.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/555413998854733844/giphy_3.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/555414036150222859/giphy.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/555414072015847428/HDpce33jcID0qNAWwNv_ehWc0Rk5tACpFvx4zciiMJT3r_rmNYYQFnEd63tTnrOefr-hObrSAyd9NwxRaNry7w.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/555414104702058511/InsistentUnnaturalEmu-size_restricted.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/555414143121752103/m4Pe0.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/555414182095487006/OblongAdoredGoshawk-size_restricted.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/555414216551432202/original.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/555414249363603456/RbRL.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/555414286722400257/tenor_1.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/555414320062922752/tenor_2.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/555414371099213854/tenor_3.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/555414410810621963/tenor.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/555414447938600972/Y5o48VW.gif"
    ]
},

"красиво":{
    "response":"",
    "gifs":[
"https://cdn.discordapp.com/attachments/539086777542246400/554646163731644416/1ae5d84e6343c5a03978fe5f88d61e9b.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/554646217338912772/6e138032944a57d65ca997887c9c6717.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/554646361660719115/8f134af4fd81c8d3d3d711ef1f775fe2.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/554646403582918666/8Xa3.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/554646466950463529/9a0985904bf1cca3be1a90010fa81ff1.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/554646569543270410/20a5a0f365016c59b72d25d870764974.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/554646638094974976/58yR.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/554646696420704287/93c25bc6399ac676fec17c8b6e6ae82d.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/554646733276315660/165ea1fd36de790d7fd64b5a1fd8e5bb.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/554646778172014608/385e970fbc3889e3ea47959107c55a10.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/554646825433301002/8088dc51b812c62f03cb3636572e025b.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/554646868970176515/9783bde4e21e836cdc9d41cd258a265397a58b87_00.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/554646939673690133/48447a08b3919e3ddeec0bd840582368.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/554646992182181888/209291.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/554647045177344010/758941f0e885597f8417ae7737a4b83d.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/554647103209734155/813004de1f784a364bbfc6965acdd028b308ef71_hq.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/554647148168216582/133418388_20966059.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/554647185128554496/1474037471_ngxkaiuc.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/554647220218232833/1511638466_kaonashi.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/554647264254230530/1520085516_bandaid.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/554647298945056779/1529731680_original.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/554647459159343115/c5b910844ccadb26eb7895b5507cceb0.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/554647498342268958/d5ebf710bdd222fe23d00421eef632c9.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/554647555942907924/dd588349b5d43e425d6d0f9e6afc7998.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/554647635009470474/f66c9bcf36a7c4261e36b1dac53e271f89856ab3_hq.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/554647695806169100/image_56110413080656381477.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/554647752081014794/image_86030217040529997099.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/554647819655446528/image_861301161830001004661.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/554647872495288330/KGaU.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/554647929059672064/MajesticThinAfricanwilddog-size_restricted.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/554647980637028367/orig.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/554648032361185300/original.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/554648075642339329/tenor.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/554648116800913418/tumblr_mh3kweQ5gY1r922azo1_500.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/554648153102745600/tumblr_oi8o5utf9V1qfec8jo1_1280.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/554648192793313280/tumblr_p5hfg3g4pj1tcvan1o1_500.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/554648225798160385/ZLsN.gif"
    ]
},

"пить":{
    "response":"Приглашаю весь чат на чай/кофе!",
    "gifs":[
"https://cdn.discordapp.com/attachments/539086777542246400/554656193587707934/0c892174527564c9df8d95314deaeaa1.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/554656239209152533/01b0b4d6c056793661de7911b6394e34.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/554656278010658816/1.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/554656329210396673/1dad4a9fcb8a81975fc8473144c09ee2448d32f1_hq.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/554656759281876992/2ZzU.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/554656799492538408/966p.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/554656833294565376/1474887049_2369.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/554656873329197058/1506572637_415d6ce4e9f7d183df4708d8d4c8f2f8.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/554656950764306453/1532761181_dsada.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/554656987548221450/15339853454650.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/554657028610719744/171700590000201.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/554657061913493515/cafe-invierno.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/554657101058670595/df7b8a399669df4e4b15d4a6b0e023f7e053a17b_hq.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/554657139688341504/DWYs.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/554657223221968906/ecd63c6a0e4aad11d688500ca22b238127828a50_hq.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/554657263281897472/FPTb.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/554657372883124246/giphy_2.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/555411661461258270/giphy.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/555411731338362881/gplus-1079159951.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/555411785885417492/GQbT.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/555412125523378186/K1nG.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/555412166363185174/large.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/555412215650320395/neK.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/555412260881825800/orig_1.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/555412484110942237/orig.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/555412705088110592/PositiveUnconsciousAffenpinscher-max-1mb.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/555412749593608224/SmoothCarefulHedgehog-small.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/555412796377006080/tenor_1.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/555412868325965835/tenor.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/555412919911841812/tumblr_m8mv1yHg5R1qeyvrko1_500.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/555412956268199976/tumblr_o5j2xsInzj1uxvvvzo1_500.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/555412998433406976/tumblr_o8mtimZl1R1rbud4zo1_500.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/555413040061743144/tumblr_o98hjyUsud1rjrmhwo1_500.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/555413081656655892/tumblr_ohfi85Rdj31vj3zbeo1_500.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/555413130268770335/tumblr_oiykk1PZrE1vj3zbeo1_r3_540.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/555413191966982145/tumblr_oog2mkfVNe1uxvvvzo1_500.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/555413236380467220/tumblr_oyx0sqMabt1w86w6ho1_500.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/555413271285596160/tumblr_p3rshjgrOi1uxvvvzo1_500.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/555413307800944688/tumblr_p7ruvgctV31wg7k9po1_500.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/555413348162732032/tumblr_pawjo9ItSz1x6a7yto1_500.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/555413385186115584/tumblr_pgbbdsr3GG1vhi5gs_640.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/555413426428706861/tumblr_pgsjscw5YQ1wfazcjo1_500.gif"
    ]
},

"спать":{
    "response":"Милый котик {author} ушёл крепко спать! Спокойно ночи, кисуля :з",
    "gifs":[
"https://cdn.discordapp.com/attachments/539086777542246400/555415256659263554/1b13f6010070fa85a49c8210d4a7d7827216a272_hq.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/555415294496210996/3c7848d9a80168db34a940aa9b768794.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/555415325768941569/4c10e10f6312d6ba8045ff911bd2cd1ce0289cf6_hq.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/555415373499990026/243e2f0cf4ad9ef9fb9def7594ec2c85.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/555415406853095434/16698d422f7483839ccb75dc7ba8a6703222c5eb_hq.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/555415481654312961/171021_2456.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/555415509244575784/1505663622_VeneratedLimpingCaimanlizard-size_restricted.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/555415555482320937/a76c8cb2735d2da97c2ff1a835e9a9fe.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/555415585870184459/anime-sleep-gif-6.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/555415617478328342/anime-sleeping-girl-gif-6.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/555415650022195210/c3bc10f31eca300f1d5ea035cf32df43.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/555415699070255124/cc17fc8fbf09ffdede87416977b97f8b05dc242f_hq.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/555415735632134155/comment_JEUs22wHIC0GhrF0oHdBoPQMCr27nB9v.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/555415787322605583/community_image_1427439103.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/555415819866341387/e7d820df79f40685c63b549009b96c71.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/555415850354737152/e8c97807ab96a5d38631934cd73231e985ebbe6c_hq.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/555415882533306429/EvergreenSociableAnemonecrab-small.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/555415921548722187/gi1212phy.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/555415956051066900/giphy_1.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/555415988707786766/HUH4AfN.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/555416028268724224/LittleWitchAcademia-Episode2-Omake-1.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/555416064079429632/mpfSC7f.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/555416113681530890/orig.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/555416151623204864/original_1.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/555416182811918346/original.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/555416215208591370/S00v.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/555416362743365632/tenor.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/555416394351771667/UglyWhichCuttlefish-small.gif",
"https://cdn.discordapp.com/attachments/539086777542246400/555416432247046144/xR1eJwS.gif"
    ]
}

}



punch_list = ['https://media.giphy.com/media/1n753Z1ZeGdkwxtYHo/giphy.gif',
               'https://media.giphy.com/media/WgN70xgCycyg2ZC5G6/giphy.gif',
               'https://media.giphy.com/media/orU5Hg8KwR430W7GIs/giphy.gif',
               'https://media.giphy.com/media/PiieOBhf5ymvOVxnzm/giphy.gif',
               'https://media.giphy.com/media/Xpj8gSHOCxONPz19AV/giphy.gif',
               'https://media.giphy.com/media/YxwAwiJEqEoFi/giphy.gif']

drink_list = ['https://media.giphy.com/media/1xlqPePKvCM3xVkWet/giphy.gif',
              'https://media.giphy.com/media/9rlYebzurMAXNaBGUO/giphy.gif',
              'https://media.giphy.com/media/1zlE7BBo7BuwpKfA4Z/giphy.gif',
              'https://media.giphy.com/media/nKMYwijvNrRwQJtq6W/giphy.gif',
              'https://media.giphy.com/media/eeLJdyAGPjnChKSlhu/giphy.gif',
              'https://media.giphy.com/media/55ma8eHi4YPCz6IZZO/giphy.gif',
              'https://media.giphy.com/media/NSqNZRkKShyKtedi0c/giphy.gif',
              'https://media.giphy.com/media/1BfhcYJtmPsM81JaRR/giphy.gif']

hug_list = [
"https://media.giphy.com/media/EvYHHSntaIl5m/giphy.gif",
"https://media.giphy.com/media/lXiRKBj0SAA0EWvbG/giphy.gif",
"https://media.giphy.com/media/xT0Gqne4C3IxaBcOdy/giphy.gif",
#"https://media.giphy.com/media/gnXG2hODaCOru/giphy.gif",
"https://media.giphy.com/media/VGACXbkf0AeGs/giphy.gif",
"https://media.giphy.com/media/l378uBCYt1vfaj2aA/giphy.gif",
"https://media.giphy.com/media/26FeTvBUZErLbTonS/giphy.gif",
"https://media.giphy.com/media/l4FGy5UyZ1KnVZ7BC/giphy.gif",
"https://media.giphy.com/media/3oz8xt8ebVWCWujyZG/giphy.gif",
"https://media.giphy.com/media/l0HlOvJ7yaacpuSas/giphy.gif",
"https://media.giphy.com/media/3otPozEs14AOGrdcOI/giphy.gif",
#"https://media.giphy.com/media/DjoWze0Patl1m/giphy.gif",
"https://media.giphy.com/media/3o6Mb7KaEIURtCKAbS/giphy.gif",
"https://media.giphy.com/media/w09VX7IEsoX6w/giphy.gif",
"https://media.giphy.com/media/vL1meInBzYCgo/giphy.gif",
"https://media.giphy.com/media/oVr48mIz8l5XG/giphy.gif",
"https://media.giphy.com/media/mmPgxbuPiwCQg/giphy.gif",
"https://media.giphy.com/media/3EJsCqoEiq6n6/giphy.gif",
"https://media.giphy.com/media/Ilkurs1e3hP0c/giphy.gif",
"https://media.giphy.com/media/jOoxG4mWGuH9S/giphy.gif",
"https://media.giphy.com/media/3orif2vpZbXi8P0fPW/giphy.gif",
"https://media.giphy.com/media/l4KhMHSclwbAGzGeI/giphy.gif",
"https://media.giphy.com/media/13fQ3RrUjteykw/giphy.gif",
"https://media.giphy.com/media/3ornk7CaGmo2uuxiJW/giphy.gif",
"https://media.giphy.com/media/xT1XGNlkcBDSqkCRqg/giphy.gif",
"https://media.giphy.com/media/l2JJySFVazmR38Lks/giphy.gif",
"https://media.giphy.com/media/3o7WTDVMidWRDzP9ss/giphy.gif",
"https://media.giphy.com/media/mLYVrZR44EcU0/giphy.gif",
"https://media.giphy.com/media/13YrHUvPzUUmkM/giphy.gif",
"https://media.giphy.com/media/du8yT5dStTeMg/giphy.gif",
"https://media.giphy.com/media/BXrwTdoho6hkQ/giphy.gif",
"https://media.giphy.com/media/qscdhWs5o3yb6/giphy.gif",
"https://media.giphy.com/media/xJlOdEYy0r7ZS/giphy.gif",
"https://media.giphy.com/media/od5H3PmEG5EVq/giphy.gif",
"https://media.giphy.com/media/svXXBgduBsJ1u/giphy.gif",
"https://media.giphy.com/media/wnsgren9NtITS/giphy.gif",
"https://media.giphy.com/media/NZ8dp5kWRbM4g/giphy.gif",
"https://media.giphy.com/media/kFTKQfjK4ysZq/giphy.gif",
"https://media.giphy.com/media/49mdjsMrH7oze/giphy.gif",
"https://media.giphy.com/media/aD1fI3UUWC4/giphy.gif",
"https://media.giphy.com/media/5eyhBKLvYhafu/giphy.gif",
"https://media.giphy.com/media/ddGxYkb7Fp2QRuTTGO/giphy.gif",
"https://media.giphy.com/media/l2QDM9Jnim1YVILXa/giphy.gif",
"https://media.giphy.com/media/ZRI1k4BNvKX1S/giphy.gif",
"https://media.giphy.com/media/s31WaGPAmTP1e/giphy.gif",
"https://media.giphy.com/media/wSY4wcrHnB0CA/giphy.gif",
"https://media.giphy.com/media/C4gbG94zAjyYE/giphy.gif",
"https://media.giphy.com/media/kvKFM3UWg2P04/giphy.gif",
"https://media.giphy.com/media/rSNAVVANV5XhK/giphy.gif",
"https://media.giphy.com/media/HaC1WdpkL3W00/giphy.gif",
"https://media.giphy.com/media/eMpDBxxTzKety/giphy.gif",
"https://media.giphy.com/media/DjczAlIcyK1Co/giphy.gif",
"https://media.giphy.com/media/yziFo5qYAOgY8/giphy.gif",
"https://media.giphy.com/media/iMrHFdDEoxT5S/giphy.gif",
"https://media.giphy.com/media/NZ8dp5kWRbM4g/giphy.gif",
"https://media.giphy.com/media/fFC10O3zlGfe/giphy.gif",
"https://media.giphy.com/media/aD1fI3UUWC4/giphy.gif",
"https://media.giphy.com/media/ZQN9jsRWp1M76/giphy.gif",
"https://media.giphy.com/media/TdXxcoNvHDVu0/giphy.gif",
"https://media.giphy.com/media/oTiuuAuYb22KQ/giphy.gif",
"https://media.giphy.com/media/11WhdeCxSM5lyo/giphy.gif",
"https://media.giphy.com/media/DjczAlIcyK1Co/giphy.gif"
]

sex_list = [
'https://discord.band/gif/1.gif',
'https://discord.band/gif/2.gif',
'https://discord.band/gif/3.gif',
'https://discord.band/gif/5.gif',
'https://discord.band/gif/6.gif',
'https://discord.band/gif/7.gif',
'https://discord.band/gif/8.gif',
'https://discord.band/gif/9.gif',
'https://discord.band/gif/10.gif',
'https://discord.band/gif/11.gif',
'https://discord.band/gif/12.gif',
'https://discord.band/gif/13.gif',
'https://discord.band/gif/14.gif',
'https://discord.band/gif/15.gif',
'https://discord.band/gif/16.gif'
]

kiss_list = [
#"https://media.giphy.com/media/KMuPz4KDkJuBq/giphy.gif",
"https://media.giphy.com/media/PFjXmKuwQsS9q/giphy.gif",
"https://media.giphy.com/media/3o7qDVQ2GrFAf1MVgc/giphy.gif",
"https://media.giphy.com/media/bCY7hoYdXmD4c/giphy.gif",
"https://media.giphy.com/media/HKQZgx0FAipPO/giphy.gif",
"https://media.giphy.com/media/l2Je2M4Nfrit0L7sQ/giphy.gif",
"https://media.giphy.com/media/3o6ozHbQHZzDTxRjsA/giphy.gif",
"https://media.giphy.com/media/3og0IvIXD1UrcEvNmw/giphy.gif",
"https://media.giphy.com/media/l0HU2EeywKGaMJCY8/giphy.gif",
"https://media.giphy.com/media/HN4Om0tu8y7gk/giphy.gif",
"https://media.giphy.com/media/3o7TKzkCiuW3E0Gn4Y/giphy.gif",
#"https://media.giphy.com/media/l0MYLr8Qh3opXBSSI/giphy.gif",
"https://media.giphy.com/media/26ufmeUh9YOVS53Xi/giphy.gif",
"https://media.giphy.com/media/26tnbo7HDeYacLQK4/giphy.gif",
"https://media.giphy.com/media/l0MYEw4RMBirPQhHy/giphy.gif",
"https://media.giphy.com/media/xThtaig5DpJpA1wuOs/giphy.gif",
"https://media.giphy.com/media/4GLJbNy3DdXPi/giphy.gif",
"https://media.giphy.com/media/2stFpADPSpfQQ/giphy.gif",
"https://media.giphy.com/media/3oAt2gl4VpnHiDW7hC/giphy.gif",
"https://media.giphy.com/media/KH1CTZtw1iP3W/giphy.gif",
"https://media.giphy.com/media/l0ErEXpCoUcS15UNq/giphy.gif",
#"https://media.giphy.com/media/1041PhUHlC0tJC/giphy.gif",
"https://media.giphy.com/media/3o6ZsXco9ACON6dSjS/giphy.gif",
"https://media.giphy.com/media/3oz8xIZrAhijabg69a/giphy.gif",
"https://media.giphy.com/media/7JaFQzMXdw759xdvpk/giphy.gif",
"https://media.giphy.com/media/3o6gDXMurw9nM2vLR6/giphy.gif",
"https://media.giphy.com/media/CzCi6itPr3yBa/giphy.gif",
"https://media.giphy.com/media/mGAzm47irxEpG/giphy.gif",
"https://media.giphy.com/media/hnNyVPIXgLdle/giphy.gif",
"https://media.giphy.com/media/f5vXCvhSJsZxu/giphy.gif",
"https://media.giphy.com/media/ZRSGWtBJG4Tza/giphy.gif",
"https://media.giphy.com/media/11k3oaUjSlFR4I/giphy.gif",
"https://media.giphy.com/media/JynbO9pnGxPrO/giphy.gif",
"https://media.giphy.com/media/nyGFcsP0kAobm/giphy.gif",
"https://media.giphy.com/media/4MBsFo1nSCfOo/giphy.gif",
#"https://media.giphy.com/media/Ch5UXfXJ3xbNK/giphy.gif",
"https://media.giphy.com/media/BaEE3QOfm2rf2/giphy.gif",
"https://media.giphy.com/media/uSHX6qYv1M7pC/giphy.gif",
"https://media.giphy.com/media/FqBTvSNjNzeZG/giphy.gif",
"https://media.giphy.com/media/EP9YxsbmbplIs/giphy.gif",
"https://media.giphy.com/media/OSq9souL3j5zW/giphy.gif",
"https://media.giphy.com/media/sS7Jac8n7L3Ve/giphy.gif",
"https://media.giphy.com/media/9P8t4wusRUdSE/giphy.gif",
"https://media.giphy.com/media/EVODaJHSXZGta/giphy.gif",
"https://media.giphy.com/media/wOtkVwroA6yzK/giphy.gif",
"https://media.giphy.com/media/fHtb1JPbfph72/giphy.gif",
#"https://media.giphy.com/media/A5FtN4L0Yp2dq/giphy.gif",
"https://media.giphy.com/media/pwZ2TLSTouCQw/giphy.gif",
"https://media.giphy.com/media/K4VEsbuHfcj6g/giphy.gif",
"https://media.giphy.com/media/HWIe1Vrs6QxFe/giphy.gif",
"https://media.giphy.com/media/tJmYMnwlvRxdK/giphy.gif",
"https://media.giphy.com/media/rSBJ7muTr25ry/giphy.gif",
"https://media.giphy.com/media/wHbQ7IMBrgTzq/giphy.gif",
"https://media.giphy.com/media/EPQDbdvqne1rM6hel8/giphy.gif",
"https://media.giphy.com/media/JFmIDQodMScJW/giphy.gif",
"https://media.giphy.com/media/ll5leTSPh4ocE/giphy.gif",
"https://media.giphy.com/media/Y9iiZdUaNRF2U/giphy.gif",
"https://media.giphy.com/media/jR22gdcPiOLaE/giphy.gif",
"https://media.giphy.com/media/CTo4IKRN4l4SA/giphy.gif",
"https://media.giphy.com/media/CRSuLR6rhDdT2/giphy.gif",
#"https://media.giphy.com/media/r1FBFMAOo8Mhy/giphy.gif",
"https://media.giphy.com/media/kU586ictpGb0Q/giphy.gif",
"https://media.giphy.com/media/bm2O3nXTcKJeU/giphy.gif",
"https://media.giphy.com/media/Ka2NAhphLdqXC/giphy.gif",
"https://media.giphy.com/media/dP8ONh1mN8YWQ/giphy.gif",
"https://media.giphy.com/media/L3rumss7XR4QM/giphy.gif",
"https://media.giphy.com/media/IdzovcoOUoUM0/giphy.gif",
"https://media.giphy.com/media/10r6oEoT6dk7E4/giphy.gif",
#"https://media.giphy.com/media/1VBRxFrg0hZ9C/giphy.gif",
#"https://media.giphy.com/media/Q1TXCgzvfLNbW/giphy.gif",
"https://media.giphy.com/media/8rE47U8UH1yEi9SI0o/giphy.gif",
#"https://media.giphy.com/media/nO8kxVKdXSaek/giphy.gif",
"https://media.giphy.com/media/s09VXOiOg79As/giphy.gif",
"https://media.giphy.com/media/G3va31oEEnIkM/giphy.gif",
"https://media.giphy.com/media/7QkZap9kQ1iy4/giphy.gif"
]

wink_list = ['https://media.discordapp.net/attachments/436139161070731264/462679150163918849/orig.gif',
             'https://cdn.discordapp.com/attachments/436139161070731264/462679245945307146/giphy-1.gif',
             'https://cdn.discordapp.com/attachments/436139161070731264/462679323506245632/girls_winking_02.gif',
             'https://cdn.discordapp.com/attachments/436139161070731264/462679514330431488/girls_winking_16.gif',
             'https://cdn.discordapp.com/attachments/436139161070731264/462679850553966602/tenor.gif']

fuck_list = ['https://media.giphy.com/media/9DayfKDecuCwUMRs38/giphy.gif',
             'https://media.giphy.com/media/621mG5MkWcAX00a5J4/giphy.gif',
             'https://media.giphy.com/media/29MEDvCpkzMMCvuZB5/giphy.gif',
             'https://media.giphy.com/media/cUVsttxcdKJJVRiFAd/giphy.gif',
             'https://media.giphy.com/media/PQxjfWa751RVJTtkS5/giphy.gif',
             'https://media.giphy.com/media/9J6Rye3Fz0Dq0oHeVH/giphy.gif']

five_list = [
'https://media.giphy.com/media/4H70la8QkZfaUvV9G4/giphy.gif',
'https://media.giphy.com/media/DQbDgJn2P5Wy3S1zr5/giphy.gif',
'https://media.giphy.com/media/pG5zFVdVsrQVteCbVS/giphy.gif',
'https://media.giphy.com/media/cRMGrkAyMdyeASLKqK/giphy.gif',
'https://media.giphy.com/media/4ZkpV1LyG0dvxYW2Zd/giphy.gif',
'https://media.giphy.com/media/n5GussPCZuekOaqMW3/giphy.gif',
"https://media.giphy.com/media/wrzf9P70YWLJK/giphy.gif",
"https://media.giphy.com/media/l0MYClvw1RPj1cZeo/giphy.gif",
"https://media.giphy.com/media/l0HlD43ktQ5f8fuWk/giphy.gif",
"https://media.giphy.com/media/3o85xHXqvkattTod68/giphy.gif",
"https://media.giphy.com/media/1nPJ5XLyZWdd4xFGw5/giphy.gif",
"https://media.giphy.com/media/r2BtghAUTmpP2/giphy.gif",
"https://media.giphy.com/media/l2JhwnKUuohwKLDnG/giphy.gif",
"https://media.giphy.com/media/2AlVpRyjAAN2/giphy.gif",
"https://media.giphy.com/media/YfTPHZ85fGnle/giphy.gif",
"https://media.giphy.com/media/C4lSxWjqSJLfG/giphy.gif",
"https://media.giphy.com/media/3o7TKTeL57EJdYFKBW/giphy.gif",
"https://media.giphy.com/media/2O0vM7oQMp4A0/giphy.gif",
"https://media.giphy.com/media/9wZybot8h5Nte/giphy.gif",
"https://media.giphy.com/media/diKF8kxuomAxy/giphy.gif",
"https://media.giphy.com/media/100QWMdxQJzQC4/giphy.gif",
"https://media.giphy.com/media/fLK0eUlYZoB6E/giphy.gif",
"https://media.giphy.com/media/13wHPKuKou0ndu/giphy.gif",
"https://media.giphy.com/media/uIu5b0YYpTPR6/giphy.gif",
"https://media.giphy.com/media/3oEduV4SOS9mmmIOkw/giphy.gif",
"https://media.giphy.com/media/fm4WhPMzu9hRK/giphy.gif",
"https://media.giphy.com/media/26ufmAlKt4ne2JDnq/giphy.gif",
"https://media.giphy.com/media/jG7UpdWLjoYuY/giphy.gif",
"https://media.giphy.com/media/l46CcVsDKp97gSDhm/giphy.gif",
"https://media.giphy.com/media/sSzCDRnOMaq3K/giphy.gif",
"https://media.giphy.com/media/DohrJX1h2W5RC/giphy.gif",
"https://media.giphy.com/media/13zazU4zSlJCiA/giphy.gif",
"https://media.giphy.com/media/WrGiAHYhZZYZ2/giphy.gif",
"https://media.giphy.com/media/3oEdvaba4h0I536VYQ/giphy.gif",
"https://media.giphy.com/media/l0HlSYVgZLQ1Y4GdO/giphy.gif",
"https://media.giphy.com/media/353PfIYZWFHaM/giphy.gif",
"https://media.giphy.com/media/3DZzjf7xCgb7y/giphy.gif",
"https://media.giphy.com/media/3o6gEgwAO6ojq63sbu/giphy.gif",
"https://media.giphy.com/media/3o85xspHMaZxVGbzY4/giphy.gif",
"https://media.giphy.com/media/l46ClnO4XNwTCuXsY/giphy.gif",
"https://media.giphy.com/media/26BREWfA5cRZJbMd2/giphy.gif",
"https://media.giphy.com/media/3o6Zt7hngn9xwnN7lC/giphy.gif",
"https://media.giphy.com/media/xT0xeQbBYVUPiKkzQs/giphy.gif",
"https://media.giphy.com/media/S6l0TQr5lomVG/giphy.gif",
"https://media.giphy.com/media/3o7TKMYAveUIqs3ZUk/giphy.gif",
"https://media.giphy.com/media/3o7buds9QVy5nCVCLe/giphy.gif",
"https://media.giphy.com/media/l42Pnm9RVo0ZG4EmI/giphy.gif",
"https://media.giphy.com/media/TQHyiK771gQw0/giphy.gif",
"https://media.giphy.com/media/l2R020v6spGBpGHrG/giphy.gif",
"https://media.giphy.com/media/GzCp9sGvlWKOc/giphy.gif",
"https://media.giphy.com/media/cAiBXaCjbHTry/giphy.gif",
"https://media.giphy.com/media/yUcor4CrgbrUY/giphy.gif",
"https://media.giphy.com/media/mJ8Xr2xYruvyF0QtMK/giphy.gif",
"https://media.giphy.com/media/QtJZpBnBJJew/giphy.gif",
"https://media.giphy.com/media/l41JOPMjzNoMYl71e/giphy.gif",
"https://media.giphy.com/media/gQ8qWas3GxlPq/giphy.gif",
"https://media.giphy.com/media/l2R0f2obXKscBVE1q/giphy.gif",
"https://media.giphy.com/media/x58AS8I9DBRgA/giphy.gif"
]



WORK_COOLDOWN = 1800
WORK_DELAY = 300


xp_lvlup_list = {
"10": 1,
"30": 2,
"60": 3,
"100": 4,
"150": 5,
"210": 6,
"280": 7,
"360": 8,
"450": 9,
"550": 10,
"660": 11,
"780": 12,
"910": 13,
"1050": 14,
"1200": 15,
"1360": 16,
"1530": 17,
"1710": 18,
"1900": 19,
"2100": 20,
"2310": 21,
"2530": 22,
"2760": 23,
"3000": 24,
"3250": 25,
"3510": 26,
"3780": 27,
"4060": 28,
"4350": 29,
"4650": 30,
"4960": 31,
"5280": 32,
"5610": 33,
"5950": 34,
"6300": 35,
"6660": 36,
"7030": 37,
"7410": 38,
"7800": 39,
"8200": 40,
"8610": 41,
"9030": 42,
"9460": 43,
"9900": 44,
"10350": 45,
"10810": 46,
"11280": 47,
"11760": 48,
"12250": 49,
"12750": 50,
"13260": 51,
"13780": 52,
"14310": 53,
"14850": 54,
"15400": 55,
"15960": 56,
"16530": 57,
"17110": 58,
"17700": 59,
"18300": 60,
"18910": 61,
"19530": 62,
"20160": 63,
"20800": 64,
"21450": 65,
"22110": 66,
"22780": 67,
"23460": 68,
"24150": 69,
"24850": 70,
"25560": 71,
"26280": 72,
"27010": 73,
"27750": 74,
"28500": 75,
"29260": 76,
"30030": 77,
"30810": 78,
"31600": 79,
"32400": 80,
"33210": 81,
"34030": 82,
"34860": 83,
"35700": 84,
"36550": 85,
"37410": 86,
"38280": 87,
"39160": 88,
"40050": 89,
"40950": 90,
"41860": 91,
"42780": 92,
"43710": 93,
"44650": 94,
"45600": 95,
"46560": 96,
"47530": 97,
"48510": 98,
"49500": 99,
"50500": 100
}

lvlup_image_url = "https://discord.band/images/lvlup.png"
lvlup_image_konoha_url = "https://discord.band/images/lvlupkonoha.png"


background_change_price = 1000

background_list = [
'neko.jpg',
'miku.jpg',
'stare.jpg',
'magic.jpg',
'night.jpg',
'autumn.jpg',
'kanade.jpg',
'forest.jpg',
'railway.jpg',
'adventure.jpg',
'mountains.jpg',
'schoolgirl.jpg',
'fairy_tale.jpg',
'nao_tomori.jpg',
'anime_girl.jpg',
'angel_beats.jpg',
'guilty_crown.jpg',
'yukari_yakumo.jpg',
'girl_with_wings.jpg',
'your_lie_in_april.jpg'
]

background_name_list = [
'Neko',
'Miku',
'Stare',
'Magic',
'Night',
'Autumn',
'Kanade',
'Forest',
'Railway',
'Adventure',
'Mountains',
'Schoolgirl',
'Fairy_Tale',
'Nao Tomori',
'Anime Girl',
'Angel Beats',
'Guilty Crown',
'Yukari Yakumo',
'Girl With Wings',
'Your Lie In April'
]

konoha_background_list = [
'konoha_primary.jpg'
]

konoha_background_name_list = [
'Konoha'
]


lang_filter = {
    "525360269023641631": {
        "filter": "1234567890\\`~!@#$%^&*()_+—-=|'’\"•√π÷×¶∆£€₽¢^°∆%©•◘○♂◙♀♪♫▬↨®™✓§;:][\{\}/?.«»₽> 〖〗,<–⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻⁼⁽⁾”“₀₁₂₃₄₅₆₇₈₉₊₋₌₍₎ᵃᵇᶜᵈᵉᶠᵍʰⁱʲᵏˡᵐⁿᵒᵖʳˢᵗᵘᵛʷˣʸᶻ№ї₴єіqwertyuiopasdfghjklzxcvbnmйцукенгшщзхъфывапролджэячсмитьбюё",
        "report_channel": "525360805324259333"
    }
}

async def check_words(client, message):
    serv = lang_filter.get(message.server.id)
    if not serv:
        return
    filter = serv.get("filter")
    emojis = client.get_all_emojis()
    for symbol in message.content:
        if not symbol.lower() in filter:
            if symbol in emojis_compact:
                continue
            em = discord.Embed(color=0xF44268)
            em.set_author(name=message.author.display_name, icon_url=message.author.avatar_url)
            em.description = message.content
            em.add_field(
                name="Channel",
                value=message.channel.mention,
                inline=True
            )
            em.add_field(
                name="Symbol",
                value=symbol,
                inline=True
            )
            await client.send_message(client.get_channel(serv.get("report_channel")), embed=em)
            await client.delete_message(message)
            return

# achievements = [
#
# ]



badges_obj = {
"staff": Image.open("cogs/stat/badges/staff.png").convert("RGBA"),
"partner": Image.open("cogs/stat/badges/partner.png").convert("RGBA"),
"hypesquad": Image.open("cogs/stat/badges/hypesquad.png").convert("RGBA"),
"bug_hunter": Image.open("cogs/stat/badges/bug_hunter.png").convert("RGBA"),
"nitro": Image.open("cogs/stat/badges/nitro.png").convert("RGBA"),
"boost": Image.open("cogs/stat/badges/boost.png").convert("RGBA"),
"early": Image.open("cogs/stat/badges/early.png").convert("RGBA"),
"verified": Image.open("cogs/stat/badges/verified.png").convert("RGBA"),
"youtube": Image.open("cogs/stat/badges/youtube.png").convert("RGBA"),
"twitch": Image.open("cogs/stat/badges/twitch.png").convert("RGBA")
}

badges_list = [
"staff",
"partner",
"hypesquad",
"bug_hunter",
"nitro",
"boost",
"early",
"verified",
"youtube",
"twitch"
]

async def check_badges(conn, id, _badges):
    if isinstance(_badges, str):
        _badges = _badges.lower().split(" ")
    badges = []
    for badge in _badges:
        if badge in badges_list:
            badges.append(badge)
    dat = await get_cached_badge(conn, id)
    ret = []
    if not dat or not dat["arguments"]:
        return ret
    for badge in badges:
        if badge in dat["arguments"]:
            ret.append(badge)
    return ret

async def set_badges(conn, id, _badges):
    if isinstance(_badges, str):
        _badges = _badges.lower().split(" ")
    badges = []
    for badge in _badges:
        if badge in badges_list:
            badges.append(badge)
    dat = await get_cached_badge(conn, id)
    if dat:
        if badges:
            await conn.execute("UPDATE mods SET arguments=ARRAY['{args}'] WHERE type = 'badges' AND name='{name}'".format(
                name=id,
                args="', '".join(badges)
            ))
        else:
            await conn.execute("DELETE FROM mods WHERE type = 'badges' AND name = '{name}'".format(name=id))
        pop_cached_badge(id)

async def update_badges(conn, id, _badges):
    if isinstance(_badges, str):
        _badges = _badges.lower().split(" ")
    badges = []
    for badge in _badges:
        if badge in badges_list:
            badges.append(badge)
    dat = await get_cached_badge(conn, id)
    if dat:
        for badge in dat["arguments"]:
            if badge in badges_list and not badge in badges:
                badges.append(badge)
        await conn.execute("UPDATE mods SET arguments=ARRAY['{args}'] WHERE type = 'badges' AND name = '{name}'".format(
            name=id,
            args="', '".join(badges)
        ))
    else:
        await conn.execute("INSERT INTO mods(name, type, arguments) VALUES('{name}', 'badges', ARRAY['{args}'])".format(
            name=id,
            args="', '".join(badges)
        ))
    pop_cached_badge(id)

async def remove_badges(conn, id, _badges):
    if isinstance(_badges, str):
        _badges = _badges.lower().split(" ")
    badg = await get_cached_badge(conn, id)
    badges = []
    if badg:
        for badge in badg["arguments"]:
            if not badge in _badges:
                badges.append(badge)
        if badges:
            await conn.execute("UPDATE mods SET arguments=ARRAY['{args}'] WHERE type = 'badges' AND name='{name}'".format(
                name=id,
                args="', '".join(badges)
            ))
        else:
            await conn.execute("DELETE FROM mods WHERE type = 'badges' AND name = '{name}'".format(name=id))
        pop_cached_badge(id)



global cached_servers
global cached_badges
cached_servers = {}
cached_badges = {}

async def clear_cache():
    while True:
        try:
            global cached_servers
            global cached_badges
            cached_servers = None
            cached_servers = {}
            cached_badges = None
            cached_badges = {}
            break
        except:
            pass
        await asyncio.sleep(10)
    await asyncio.sleep(100)

async def clear_caches():
    global cached_servers
    global cached_badges
    cached_servers = None
    cached_servers = {}
    cached_badges = None
    cached_badges = {}


async def get_cached_badge(conn, id):
    global cached_badges
    if not id in cached_badges.keys():
        dat = await conn.fetchrow("SELECT * FROM mods WHERE type = 'badges' AND name = '{id}'".format(id=id))
        if not dat:
            return None
        cached_badges[id] = dat
    return cached_badges.get(id, None)

async def get_cached_server(conn, id):
    global cached_servers
    if not id in cached_servers.keys():
        dat = await conn.fetchrow("SELECT * FROM settings WHERE discord_id = '{discord_id}'".format(discord_id=id))
        if not dat:
            return None
        cached_servers[id] = dat
    return cached_servers.get(id, None)

def pop_cached_server(id):
    global cached_servers
    return cached_servers.pop(id, None)

def pop_cached_badge(id):
    global cached_badges
    return cached_badges.pop(id, None)



prefix_list = [
    '!',
    '?',
    '$',
    't!',
    't?',
    't$',
    '.',
    '-',
    '+',
    ';',
    '>',
    '<',
    '~',
    '^',
    '=',
    '_',
    '`'
]


short_locales = {
"en": "english",
"ru": "russian",
"ua": "ukrainian"
}


ururu_responses = [
"Уруру",
"Урурушеньки",
"Урурушечки",
"Уруру))",
"Урурушеньки))",
"Урурушечки))"
]


slot_kanna = '<:kanna:491965559907418112>'
slot_pantsu1 = '<:pantsu:491967185254613023>'
slot_pantsu2 = '<:pantsu2:491965559387455506>'
slot_doge = '<:doge:491965559529930753>'
slot_trap = '<:trap:491965559806754847>'
slot_salt = '<:salt:491965559613947904>'
slot_awoo = '<:awoo:491965559748165633>'
slot_boom = '<:booom:491965559496376330>'
slot_melban = '<:banned:491965559659954201>'
slots_ver = []

i = 0
while i < 3:
    i += 1
    slots_ver.append(slot_kanna)
i = 0
while i < 40:
    i += 1
    slots_ver.append(slot_melban)
i = 0
while i < 40:
    i += 1
    slots_ver.append(slot_boom)
i = 0
while i < 5:
    i += 1
    slots_ver.append(slot_pantsu1)
i = 0
while i < 10:
    i += 1
    slots_ver.append(slot_pantsu2)
i = 0
while i < 15:
    i += 1
    slots_ver.append(slot_doge)
i = 0
while i < 20:
    i += 1
    slots_ver.append(slot_salt)
i = 0
while i < 25:
    i += 1
    slots_ver.append(slot_awoo)
i = 0
while i < 30:
    i += 1
    slots_ver.append(slot_trap)

# -------------------------------

slots_ver_boost = []

i = 0
while i < 6:
    i += 1
    slots_ver_boost.append(slot_kanna)
i = 0
while i < 30:
    i += 1
    slots_ver_boost.append(slot_melban)
i = 0
while i < 30:
    i += 1
    slots_ver_boost.append(slot_boom)
i = 0
while i < 5:
    i += 1
    slots_ver_boost.append(slot_pantsu1)
i = 0
while i < 10:
    i += 1
    slots_ver_boost.append(slot_pantsu2)
i = 0
while i < 15:
    i += 1
    slots_ver_boost.append(slot_doge)
i = 0
while i < 20:
    i += 1
    slots_ver_boost.append(slot_salt)
i = 0
while i < 25:
    i += 1
    slots_ver_boost.append(slot_awoo)
i = 0
while i < 25:
    i += 1
    slots_ver_boost.append(slot_trap)



default_message = discord.Embed(color=0xC5934B)
success_message = discord.Embed(color=0x00ff08)
error_message = discord.Embed(color=0xff3838)

default_color = 0xC5934B
success_color = 0x00ff08
error_color = 0xff3838


BR_MAX_BET = 100000
SLOTS_MAX_BET = 50000


not_log_servers = [
"264445053596991498",
"110373943822540800",
"401422952639496213",
"435863655314227211",
"450100127256936458",
"485400595235340303",
"458947364137467906"
]

log_join_leave_server_channel_id = "493196075352457247"
log_join_leave_server_id = "480689184814792704"
admin_server_id = "327029562535968768"

#             Ананасовая Печенюха   Ананасовая Печенюха        Unknown                Teris                Oddy38                                                            Nightmare
admin_list = ['528963740415295509', '554418178940338194', '499937748862500864', '281037696225247233', '496569904527441921', '500943025640439819', '502434007796023296', '323722237276454913']
#               Ананасовая Печенюха   Ананасовая Печенюха         Unknown                Teris                Oddy38              mankidelufi                                                         Nightmare
support_list = ['528963740415295509', '554418178940338194', '499937748862500864', '281037696225247233', '496569904527441921', '342557917121347585', '500943025640439819', '502434007796023296', '323722237276454913', '476949839402237953', '284346524438233089']

nazarik_id = "465616048050143232"
nazarik_log_id = "480692089332695040"

tester_role_id = "477738087212908544"

uptimes = 0


global muted_users
muted_users = {}

global top_servers
top_servers = []

old_neko_id = "475425777215864833"
new_neko_id = "525360269023641631"

# tomori_links = '[Vote](https://discordbots.org/bot/491605739635212298/vote "for Tomori") \
# [Donate](https://discord.band/donate "Donate") \
# [YouTube](https://www.youtube.com/channel/UCxqg3WZws6KxftnC-MdrIpw "Tomori Project\'s channel") \
# [Telegram](https://t.me/TomoriDiscord "Our telegram channel") \
# [Website](https://discord.band "Our website") \
# [VK](https://vk.com/tomori_discord "Our group on vk.com")'

# tomori_links = '[Join Konoha](https://discord.gg/PErt9KY "Join anime Naruto")'

tomori_links = '[Let\'s check our new Monitoring\nhttps://discordserver.info/](https://discordserver.info/ "Awesome servers list")'


def clear_name(name):
    return re.sub(r'[\';"\\]+', '', name)

def clear_text(text):
    return re.sub(r'["\\]+', '', text)



logg = logging.getLogger('tomori-debug')
logg.setLevel(logging.DEBUG)
logname = 'logs/debug.log'
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
logg.addHandler(handler)


async def get_embed(value):
    try:
        ret = json.loads(value)
        if ret and isinstance(ret, dict):
            urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', str(ret.get("author", {}).get("icon_url", "")))
            if urls:
                ret["author"]["icon_url"] = urls[0]
            else:
                if ret.get("author"):
                    ret["author"].pop("icon_url", None)
            urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', str(ret.get("author", {}).get("url", "")))
            if urls:
                ret["author"]["url"] = urls[0]
            else:
                if ret.get("author"):
                    ret["author"].pop("url", None)
            urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', str(ret.get("footer", {}).get("icon_url", "")))
            if urls:
                ret["footer"]["icon_url"] = urls[0]
            else:
                if ret.get("footer"):
                    ret["footer"].pop("icon_url", None)
            urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', str(ret.get("image", "")))
            if urls:
                ret["image"] = urls[0]
            else:
                ret.pop("image", None)
            urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', str(ret.get("thumbnail", "")))
            if urls:
                ret["thumbnail"] = urls[0]
            else:
                if ret.get("thumbnail"):
                    ret.pop("thumbnail", None)
            if ret.get("Text"):
                ret["text"] = str(ret.pop("Text", ""))
            if ret.get("title"):
                ret["title"] = str(ret["title"])[:256]
            if ret.get("description"):
                ret["description"] = str(ret["description"])[:2048]
            if ret.get("footer", {}).get("text"):
                ret["footer"]["text"] = str(ret["footer"]["text"])[:2048]
            if ret.get("author", {}).get("name"):
                ret["author"]["name"] = str(ret["author"]["name"])[:256]
            if ret.get("fields") and isinstance(ret["fields"], list):
                fields = []
                count = 0
                for field in ret["fields"]:
                    name = field.get("name")
                    value = field.get("value")
                    inline = field.get("inline")
                    if not isinstance(inline, bool):
                        continue
                    if name:
                        name = str(name)[:256]
                    else:
                        continue
                    if value:
                        value = str(value)[:1024]
                    else:
                        continue
                    count += 1
                    fields.append({
                        "name": name,
                        "value": value,
                        "inline": inline
                    })
                    if count == 25:
                        break
                ret["fields"] = fields

            em = discord.Embed(**ret)
            if "author" in ret.keys():
                em.set_author(
                    name=ret["author"].get("name"),
                    url=ret["author"].get("url", discord.Embed.Empty),
                    icon_url=ret["author"].get("icon_url", discord.Embed.Empty)
                )
            if "footer" in ret.keys():
                em.set_footer(
                    text=ret["footer"].get("text", discord.Embed.Empty),
                    icon_url=ret["footer"].get("icon_url", discord.Embed.Empty)
                )
            if "image" in ret.keys():
                em.set_image(
                    url=ret["image"]
                )
            if "thumbnail" in ret.keys():
                em.set_thumbnail(
                    url=ret["thumbnail"]
                )
            if "fields" in ret.keys():
                for field in ret["fields"]:
                    try:
                        em.add_field(
                            name=field.get("name"),
                            value=field.get("value"),
                            inline=field.get("inline", False)
                        )
                    except:
                        pass
        if "text" in ret.keys():
            text = ret["text"]
        else:
            text = None
    except:
        text = value[:2000]
        em = None
    return text, em


async def dict_to_embed(ret):
    try:
        if ret:
            urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', str(ret.get("author", {}).get("icon_url", "")))
            if urls:
                ret["author"]["icon_url"] = urls[0]
            else:
                if ret.get("author"):
                    ret["author"].pop("icon_url", None)
            urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', str(ret.get("author", {}).get("url", "")))
            if urls:
                ret["author"]["url"] = urls[0]
            else:
                if ret.get("author"):
                    ret["author"].pop("url", None)
            urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', str(ret.get("footer", {}).get("icon_url", "")))
            if urls:
                ret["footer"]["icon_url"] = urls[0]
            else:
                if ret.get("footer"):
                    ret["footer"].pop("icon_url", None)
            urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', str(ret.get("image", "")))
            if urls:
                ret["image"] = urls[0]
            else:
                ret.pop("image", None)
            urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', str(ret.get("thumbnail", "")))
            if urls:
                ret["thumbnail"] = urls[0]
            else:
                if ret.get("thumbnail"):
                    ret.pop("thumbnail", None)
            if ret.get("Text"):
                ret["text"] = str(ret.pop("Text", ""))
            if ret.get("title"):
                ret["title"] = str(ret["title"])[:256]
            if ret.get("description"):
                ret["description"] = str(ret["description"])[:2048]
            if ret.get("footer", {}).get("text"):
                ret["footer"]["text"] = str(ret["footer"]["text"])[:2048]
            if ret.get("author", {}).get("name"):
                ret["author"]["name"] = str(ret["author"]["name"])[:256]
            if ret.get("fields") and isinstance(ret["fields"], list):
                fields = []
                count = 0
                for field in ret["fields"]:
                    name = field.get("name")
                    value = field.get("value")
                    inline = field.get("inline")
                    if not isinstance(inline, bool):
                        continue
                    if name:
                        name = str(name)[:256]
                    else:
                        continue
                    if value:
                        value = str(value)[:1024]
                    else:
                        continue
                    count += 1
                    fields.append({
                        "name": name,
                        "value": value,
                        "inline": inline
                    })
                    if count == 25:
                        break
                ret["fields"] = fields

            em = discord.Embed(**ret)
            if not em:
                raise
            if "author" in ret.keys():
                em.set_author(
                    name=ret["author"].get("name"),
                    url=ret["author"].get("url", discord.Embed.Empty),
                    icon_url=ret["author"].get("icon_url", discord.Embed.Empty)
                )
            if "footer" in ret.keys():
                em.set_footer(
                    text=ret["footer"].get("text", discord.Embed.Empty),
                    icon_url=ret["footer"].get("icon_url", discord.Embed.Empty)
                )
            if "image" in ret.keys():
                em.set_image(
                    url=ret["image"]
                )
            if "thumbnail" in ret.keys():
                em.set_thumbnail(
                    url=ret["thumbnail"]
                )
            if "fields" in ret.keys():
                for field in ret["fields"]:
                    em.add_field(
                        name=field.get("name"),
                        value=field.get("value"),
                        inline=field.get("inline", False)
                    )
        if "text" in ret.keys():
            text = ret["text"]
        else:
            text = None
    except:
        text = str(ret)[:2000]
        em = None
    return text, em






errors = {
    "user_in_not_exists_guild": "Guild Error 404",
    "guild_remove_not_exists": "Guild Error 500",
    "guild_info_not_exists": "Guild Error 403",
    "guild_join_member_not_exists": "Guild Error 99",
    "guild_accept_bad_response": "Guild Error 69"
}




captcha_list = {
    "ȚÖMÖŖÏ": "tomori",
    "•´¯`•. t๏๓๏гเ .•´¯`•": "tomori",
    "ŤỖϻỖŘĮ": "tomori",
    "ČỖỖЌĮẸ": "cookie",
    "cooĸιe": "cookie",
    "ȼ๏๏Ќɨ€": "cookie",
    "𝕿𝖔𝖒𝖔𝖗𝖎": "tomori",
    "🌴⚽〽️⚽🌱🎐": "tomori",
    "🆃🅾🅼🅾🆁🅸": "tomori",
    "ᗫᓿSᑤᓎᖇᗫ": "discord",
    "ÐɪらㄈØ尺Ð": "discord",
    "ⓓⓘⓢⓒⓞⓡⓓ": "discord",
    "𝓭𝓲𝓼𝓬𝓸𝓻𝓭": "discord",
    "𝖓𝖎𝖈𝖊 𝖈𝖆𝖕𝖙𝖈𝖍𝖆": "nice captcha",
    "ᑎIᑕE ᑕᗩᑭTᑕᕼᗩ": "nice captcha",
    "ɴɪᴄᴇ ᴄᴀᴘᴛᴄʜᴀ": "nice captcha",
    "𝕀 𝕙𝕒𝕥𝕖 𝕪𝕠𝕦": "i hate you",
    "𝕴 𝖍𝖆𝖙𝖊 𝖞𝖔𝖚": "i hate you",
    "𝓘 𝓱𝓪𝓽𝓮 𝔂𝓸𝓾": "i hate you",
    "𝙄 𝙝𝙖𝙩𝙚 𝙮𝙤𝙪": "i hate you"
}

captcha_symbols = [
    "EYUIOA",
    "QWRTPSDFGHJKLZXCVBNM"
]




welcome_responses_dm = {
# ОКД (чета с ссср)
"485447833932005379": {
      "text": "Здесь описание интересностей сервера - <#490177759507775489>",
      "description": "**А правила очень просты: **\n- Нельзя нарушать законы РФ\n- Нельзя переходить на личности в оскорблениях\n- Нельзя рекламировать сервера дискорда.\n\nРады видеть вас на нашем сервере! Всего доброго!",
      "color": 12948299
    },
# КАКТАМНОВОСТИ
"496507405732020224": {
      "description": "**Добро пожаловать на новостной сервер КАКТАМНОВОСТИ.**\n\nПрежде чем ты начнешь знакомиться с остальными участниками, пожалуйста,  ознакомься с полезной информацией на канале <#496697194649223175>\n\n*Тут могут быть БУФЕРА, ТРЕШ и НЕ БУДЕТ НАСТЫРНЫХ ПРАВЕДНИКОВ, (возможно).\nНадеюсь тебе у нас понравится!\nЖелаем приятного время КАКТАМпровождения.*\n\nЧто ж, веселись и приглашай друзей! :blush:\nПокедова, увидимся на сервере :heart: ",
      "author": {
        "name": "КАКТАМНОВОСТИ",
        "icon_url": "https://images-ext-2.discordapp.net/external/Nne3hrU-e2gDmobjirCrOJO3dVfeTSiYx6Y2l4cf1EE/https/cdn.discordapp.com/icons/496507405732020224/5c81c2acec3621896e4a7f1a15947975.jpg"
      },
      "color": 3553599
    },
# Neko.land
"475425777215864833": {
    "description": "Мы переехали, подробнее на новом сервере <3",
    "author": {
    "name": "Новый неколенд"
    },
    "color": 53380,
    "image": "https://gifimage.net/wp-content/uploads/2017/09/anime-neko-girl-gif-9.gif",
    "fields": [
        {
          "name": "Ссылка",
          "value": "https://discord.gg/yEczRp6",
          "inline": True
        }
    ]
}
}


emojis_compact = ["❆","👩‍👩‍👦","👩","😀","😁","😂","🤣","😃","😄","😅","😆","😉","😊","😋","😎","😍","😘","🥰","😗","😙","😚","☺","🙂","🤗","🤩","🤔","🤨","😐","😑","😶","🙄","😏","😣","😥","😮","🤐","😯","😪","😫","😴","😌","😛","😜","😝","🤤","😒","😓","😔","😕","🙃","🤑","😲","☹","🙁","😖","😞","😟","😤","😢","😭","😦","😧","😨","😩","🤯","😬","😰","😱","🥵","🥶","😳","🤪","😵","😡","😠","🤬","😷","🤒","🤕","🤢","🤮","🤧","😇","🤠","🥳","🥴","🥺","🤥","🤫","🤭","🧐","🤓","😈","👿","🤡","👹","👺","💀","☠","👻","👽","👾","🤖","💩","😺","😸","😹","😻","😼","😽","🙀","😿","😾","🙈","🙉","🙊","👶","🧒","👦","👧","🧑","👨","👩","🧓","👴","👵","👨‍⚕️","👩‍⚕️","👨‍🎓","👩‍🎓","👨‍🏫","👩‍🏫","👨‍⚖️","👩‍⚖️","👨‍🌾","👩‍🌾","👨‍🍳","👩‍🍳","👨‍🔧","👩‍🔧","👨‍🏭","👩‍🏭","👨‍💼","👩‍💼","👨‍🔬","👩‍🔬","👨‍💻","👩‍💻","👨‍🎤","👩‍🎤","👨‍🎨","👩‍🎨","👨‍✈️","👩‍✈️","👨‍🚀","👩‍🚀","👨‍🚒","👩‍🚒","👮","👮‍♂️","👮‍♀️","🕵","🕵️‍♂️","🕵️‍♀️","💂","💂‍♂️","💂‍♀️","👷","👷‍♂️","👷‍♀️","🤴","👸","👳","👳‍♂️","👳‍♀️","👲","🧕","🧔","👱","👱‍♂️","👱‍♀️","👨‍🦰","👩‍🦰","👨‍🦱","👩‍🦱","👨‍🦲","👩‍🦲","👨‍🦳","👩‍🦳","🤵","👰","🤰","🤱","👼","🎅","🤶","🦸","🦸‍♀️","🦸‍♂️","🦹","🦹‍♀️","🦹‍♂️","🧙","🧙‍♀️","🧙‍♂️","🧚","🧚‍♀️","🧚‍♂️","🧛","🧛‍♀️","🧛‍♂️","🧜","🧜‍♀️","🧜‍♂️","🧝","🧝‍♀️","🧝‍♂️","🧞","🧞‍♀️","🧞‍♂️","🧟","🧟‍♀️","🧟‍♂️","🙍","🙍‍♂️","🙍‍♀️","🙎","🙎‍♂️","🙎‍♀️","🙅","🙅‍♂️","🙅‍♀️","🙆","🙆‍♂️","🙆‍♀️","💁","💁‍♂️","💁‍♀️","🙋","🙋‍♂️","🙋‍♀️","🙇","🙇‍♂️","🙇‍♀️","🤦","🤦‍♂️","🤦‍♀️","🤷","🤷‍♂️","🤷‍♀️","💆","💆‍♂️","💆‍♀️","💇","💇‍♂️","💇‍♀️","🚶","🚶‍♂️","🚶‍♀️","🏃","🏃‍♂️","🏃‍♀️","💃","🕺","👯","👯‍♂️","👯‍♀️","🧖","🧖‍♀️","🧖‍♂️","🧗","🧗‍♀️","🧗‍♂️","🧘","🧘‍♀️","🧘‍♂️","🛀","🛌","🕴","🗣","👤","👥","🤺","🏇","⛷","🏂","🏌","🏌️‍♂️","🏌️‍♀️","🏄","🏄‍♂️","🏄‍♀️","🚣","🚣‍♂️","🚣‍♀️","🏊","🏊‍♂️","🏊‍♀️","⛹","⛹️‍♂️","⛹️‍♀️","🏋","🏋️‍♂️","🏋️‍♀️","🚴","🚴‍♂️","🚴‍♀️","🚵","🚵‍♂️","🚵‍♀️","🏎","🏍","🤸","🤸‍♂️","🤸‍♀️","🤼","🤼‍♂️","🤼‍♀️","🤽","🤽‍♂️","🤽‍♀️","🤾","🤾‍♂️","🤾‍♀️","🤹","🤹‍♂️","🤹‍♀️","👫","👬","👭","💏","👩‍❤️‍💋‍👨","👨‍❤️‍💋‍👨","👩‍❤️‍💋‍👩","💑","👩‍❤️‍👨","👨‍❤️‍👨","👩‍❤️‍👩","👪","👨‍👩‍👦","👨‍👩‍👧","👨‍👩‍👧‍👦","👨‍👩‍👦‍👦","👨‍👩‍👧‍👧","👨‍👨‍👦","👨‍👨‍👧","👨‍👨‍👧‍👦","👨‍👨‍👦‍👦","👨‍👨‍👧‍👧","👩‍👩‍👦","👩‍👩‍👧","👩‍👩‍👧‍👦","👩‍👩‍👦‍👦","👩‍👩‍👧‍👧","👨‍👦","👨‍👦‍👦","👨‍👧","👨‍👧‍👦","👨‍👧‍👧","👩‍👦","👩‍👦‍👦","👩‍👧","👩‍👧‍👦","👩‍👧‍👧","🤳","💪","🦵","🦶","👈","👉","☝","👆","🖕","👇","✌","🤞","🖖","🤘","🤙","🖐","✋","👌","👍","👎","✊","👊","🤛","🤜","🤚","👋","🤟","✍","👏","👐","🙌","🤲","🙏","🤝","💅","👂","👃","🦰","🦱","🦲","🦳","👣","👀","👁","👁️‍🗨️","🧠","🦴","🦷","👅","👄","💋","💘","❤","💓","💔","💕","💖","💗","💙","💚","💛","🧡","💜","🖤","💝","💞","💟","❣","💌","💤","💢","💣","💥","💦","💨","💫","💬","🗨","🗯","💭","🕳","👓","🕶","🥽","🥼","👔","👕","👖","🧣","🧤","🧥","🧦","👗","👘","👙","👚","👛","👜","👝","🛍","🎒","👞","👟","🥾","🥿","👠","👡","👢","👑","👒","🎩","🎓","🧢","⛑","📿","💄","💍","💎","🐵","🐒","🦍","🐶","🐕","🐩","🐺","🦊","🦝","🐱","🐈","🦁","🐯","🐅","🐆","🐴","🐎","🦄","🦓","🦌","🐮","🐂","🐃","🐄","🐷","🐖","🐗","🐽","🐏","🐑","🐐","🐪","🐫","🦙","🦒","🐘","🦏","🦛","🐭","🐁","🐀","🐹","🐰","🐇","🐿","🦔","🦇","🐻","🐨","🐼","🦘","🦡","🐾","🦃","🐔","🐓","🐣","🐤","🐥","🐦","🐧","🕊","🦅","🦆","🦢","🦉","🦚","🦜","🐸","🐊","🐢","🦎","🐍","🐲","🐉","🦕","🦖","🐳","🐋","🐬","🐟","🐠","🐡","🦈","🐙","🐚","🦀","🦞","🦐","🦑","🐌","🦋","🐛","🐜","🐝","🐞","🦗","🕷","🕸","🦂","🦟","🦠","💐","🌸","💮","🏵","🌹","🥀","🌺","🌻","🌼","🌷","🌱","🌲","🌳","🌴","🌵","🌾","🌿","☘","🍀","🍁","🍂","🍃","🍇","🍈","🍉","🍊","🍋","🍌","🍍","🥭","🍎","🍏","🍐","🍑","🍒","🍓","🥝","🍅","🥥","🥑","🍆","🥔","🥕","🌽","🌶","🥒","🥬","🥦","🍄","🥜","🌰","🍞","🥐","🥖","🥨","🥯","🥞","🧀","🍖","🍗","🥩","🥓","🍔","🍟","🍕","🌭","🥪","🌮","🌯","🥙","🥚","🍳","🥘","🍲","🥣","🥗","🍿","🧂","🥫","🍱","🍘","🍙","🍚","🍛","🍜","🍝","🍠","🍢","🍣","🍤","🍥","🥮","🍡","🥟","🥠","🥡","🍦","🍧","🍨","🍩","🍪","🎂","🍰","🧁","🥧","🍫","🍬","🍭","🍮","🍯","🍼","🥛","☕","🍵","🍶","🍾","🍷","🍸","🍹","🍺","🍻","🥂","🥃","🥤","🥢","🍽","🍴","🥄","🔪","🏺","🌍","🌎","🌏","🌐","🗺","🗾","🧭","🏔","⛰","🌋","🗻","🏕","🏖","🏜","🏝","🏞","🏟","🏛","🏗","🧱","🏘","🏚","🏠","🏡","🏢","🏣","🏤","🏥","🏦","🏨","🏩","🏪","🏫","🏬","🏭","🏯","🏰","💒","🗼","🗽","⛪","🕌","🕍","⛩","🕋","⛲","⛺","🌁","🌃","🏙","🌄","🌅","🌆","🌇","🌉","♨","🌌","🎠","🎡","🎢","💈","🎪","🚂","🚃","🚄","🚅","🚆","🚇","🚈","🚉","🚊","🚝","🚞","🚋","🚌","🚍","🚎","🚐","🚑","🚒","🚓","🚔","🚕","🚖","🚗","🚘","🚙","🚚","🚛","🚜","🚲","🛴","🛹","🛵","🚏","🛣","🛤","🛢","⛽","🚨","🚥","🚦","🛑","🚧","⚓","⛵","🛶","🚤","🛳","⛴","🛥","🚢","✈","🛩","🛫","🛬","💺","🚁","🚟","🚠","🚡","🛰","🚀","🛸","🛎","🧳","⌛","⏳","⌚","⏰","⏱","⏲","🕰","🕛","🕧","🕐","🕜","🕑","🕝","🕒","🕞","🕓","🕟","🕔","🕠","🕕","🕡","🕖","🕢","🕗","🕣","🕘","🕤","🕙","🕥","🕚","🕦","🌑","🌒","🌓","🌔","🌕","🌖","🌗","🌘","🌙","🌚","🌛","🌜","🌡","☀","🌝","🌞","⭐","🌟","🌠","☁","⛅","⛈","🌤","🌥","🌦","🌧","🌨","🌩","🌪","🌫","🌬","🌀","🌈","🌂","☂","☔","⛱","⚡","❄","☃","⛄","☄","🔥","💧","🌊","🎃","🎄","🎆","🎇","🧨","✨","🎈","🎉","🎊","🎋","🎍","🎎","🎏","🎐","🎑","🧧","🎀","🎁","🎗","🎟","🎫","🎖","🏆","🏅","🥇","🥈","🥉","⚽","⚾","🥎","🏀","🏐","🏈","🏉","🎾","🥏","🎳","🏏","🏑","🏒","🥍","🏓","🏸","🥊","🥋","🥅","⛳","⛸","🎣","🎽","🎿","🛷","🥌","🎯","🎱","🔮","🧿","🎮","🕹","🎰","🎲","🧩","🧸","♠","♥","♦","♣","♟","🃏","🀄","🎴","🎭","🖼","🎨","🧵","🧶","🔇","🔈","🔉","🔊","📢","📣","📯","🔔","🔕","🎼","🎵","🎶","🎙","🎚","🎛","🎤","🎧","📻","🎷","🎸","🎹","🎺","🎻","🥁","📱","📲","☎","📞","📟","📠","🔋","🔌","💻","🖥","🖨","⌨","🖱","🖲","💽","💾","💿","📀","🧮","🎥","🎞","📽","🎬","📺","📷","📸","📹","📼","🔍","🔎","🕯","💡","🔦","🏮","📔","📕","📖","📗","📘","📙","📚","📓","📒","📃","📜","📄","📰","🗞","📑","🔖","🏷","💰","💴","💵","💶","💷","💸","💳","🧾","💹","💱","💲","✉","📧","📨","📩","📤","📥","📦","📫","📪","📬","📭","📮","🗳","✏","✒","🖋","🖊","🖌","🖍","📝","💼","📁","📂","🗂","📅","📆","🗒","🗓","📇","📈","📉","📊","📋","📌","📍","📎","🖇","📏","📐","✂","🗃","🗄","🗑","🔒","🔓","🔏","🔐","🔑","🗝","🔨","⛏","⚒","🛠","🗡","⚔","🔫","🏹","🛡","🔧","🔩","⚙","🗜","⚖","🔗","⛓","🧰","🧲","⚗","🧪","🧫","🧬","🔬","🔭","📡","💉","💊","🚪","🛏","🛋","🚽","🚿","🛁","🧴","🧷","🧹","🧺","🧻","🧼","🧽","🧯","🛒","🚬","⚰","⚱","🗿","🏧","🚮","🚰","♿","🚹","🚺","🚻","🚼","🚾","🛂","🛃","🛄","🛅","⚠","🚸","⛔","🚫","🚳","🚭","🚯","🚱","🚷","📵","🔞","☢","☣","⬆","↗","➡","↘","⬇","↙","⬅","↖","↕","↔","↩","↪","⤴","⤵","🔃","🔄","🔙","🔚","🔛","🔜","🔝","🛐","⚛","🕉","✡","☸","☯","✝","☦","☪","☮","🕎","🔯","♈","♉","♊","♋","♌","♍","♎","♏","♐","♑","♒","♓","⛎","🔀","🔁","🔂","▶","⏩","⏭","⏯","◀","⏪","⏮","🔼","⏫","🔽","⏬","⏸","⏹","⏺","⏏","🎦","🔅","🔆","📶","📳","📴","♀","♂","⚕","♾","♻","⚜","🔱","📛","🔰","⭕","✅","☑","✔","✖","❌","❎","➕","➖","➗","➰","➿","〽","✳","✴","❇","‼","⁉","❓","❔","❕","❗","〰","©","®","™","#️⃣","*️⃣","0️⃣","1️⃣","2️⃣","3️⃣","4️⃣","5️⃣","6️⃣","7️⃣","8️⃣","9️⃣","🔟","💯","🔠","🔡","🔢","🔣","🔤","🅰","🆎","🅱","🆑","🆒","🆓","ℹ","🆔","Ⓜ","🆕","🆖","🅾","🆗","🅿","🆘","🆙","🆚","🈁","🈂","🈷","🈶","🈯","🉐","🈹","🈚","🈲","🉑","🈸","🈴","🈳","㊗","㊙","🈺","🈵","▪","▫","◻","◼","◽","◾","⬛","⬜","🔶","🔷","🔸","🔹","🔺","🔻","💠","🔘","🔲","🔳","⚪","⚫","🔴","🔵","🏁","🚩","🎌","🏴","🏳","🏳️‍🌈","🏳️‍","�","🏴‍☠️","🇦🇨","🇦🇩","🇦🇪","🇦🇫","🇦🇬","🇦🇮","🇦🇱","🇦🇲","🇦🇴","🇦🇶","🇦🇷","🇦🇸","🇦🇹","🇦🇺","🇦🇼","🇦🇽","🇦🇿","🇧🇦","🇧🇧","🇧🇩","🇧🇪","🇧🇫","🇧🇬","🇧🇭","🇧🇮","🇧🇯","🇧🇱","🇧🇲","🇧🇳","🇧🇴","🇧🇶","🇧🇷","🇧🇸","🇧🇹","🇧🇻","🇧🇼","🇧🇾","🇧🇿","🇨🇦","🇨🇨","🇨🇩","🇨🇫","🇨🇬","🇨🇭","🇨🇮","🇨🇰","🇨🇱","🇨🇲","🇨🇳","🇨🇴","🇨🇵","🇨🇷","🇨🇺","🇨🇻","🇨🇼","🇨🇽","🇨🇾","🇨🇿","🇩🇪","🇩🇬","🇩🇯","🇩🇰","🇩🇲","🇩🇴","🇩🇿","🇪🇦","🇪🇨","🇪🇪","🇪🇬","🇪🇭","🇪🇷","🇪🇸","🇪🇹","🇪🇺","🇫🇮","🇫🇯","🇫🇰","🇫🇲","🇫🇴","🇫🇷","🇬🇦","🇬🇧","🇬🇩","🇬🇪","🇬🇫","🇬🇬","🇬🇭","🇬🇮","🇬🇱","🇬🇲","🇬🇳","🇬🇵","🇬🇶","🇬🇷","🇬🇸","🇬🇹","🇬🇺","🇬🇼","🇬🇾","🇭🇰","🇭🇲","🇭🇳","🇭🇷","🇭🇹","🇭🇺","🇮🇨","🇮🇩","🇮🇪","🇮🇱","🇮🇲","🇮🇳","🇮🇴","🇮🇶","🇮🇷","🇮🇸","🇮🇹","🇯🇪","🇯🇲","🇯🇴","🇯🇵","🇰🇪","🇰🇬","🇰🇭","🇰🇮","🇰🇲","🇰🇳","🇰🇵","🇰🇷","🇰🇼","🇰🇾","🇰🇿","🇱🇦","🇱🇧","🇱🇨","🇱🇮","🇱🇰","🇱🇷","🇱🇸","🇱🇹","🇱🇺","🇱🇻","🇱🇾","🇲🇦","🇲🇨","🇲🇩","🇲🇪","🇲🇫","🇲🇬","🇲🇭","🇲🇰","🇲🇱","🇲🇲","🇲🇳","🇲🇴","🇲🇵","🇲🇶","🇲🇷","🇲🇸","🇲🇹","🇲🇺","🇲🇻","🇲🇼","🇲🇽","🇲🇾","🇲🇿","🇳🇦","🇳🇨","🇳🇪","🇳🇫","🇳🇬","🇳🇮","🇳🇱","🇳🇴","🇳🇵","🇳🇷","🇳🇺","🇳🇿","🇴🇲","🇵🇦","🇵🇪","🇵🇫","🇵🇬","🇵🇭","🇵🇰","🇵🇱","🇵🇲","🇵🇳","🇵🇷","🇵🇸","🇵🇹","🇵🇼","🇵🇾","🇶🇦","🇷🇪","🇷🇴","🇷🇸","🇷🇺","🇷🇼","🇸🇦","🇸🇧","🇸🇨","🇸🇩","🇸🇪","🇸🇬","🇸🇭","🇸🇮","🇸🇯","🇸🇰","🇸🇱","🇸🇲","🇸🇳","🇸🇴","🇸🇷","🇸🇸","🇸🇹","🇸🇻","🇸🇽","🇸🇾","🇸🇿","🇹🇦","🇹🇨","🇹🇩","🇹🇫","🇹🇬","🇹🇭","🇹🇯","🇹🇰","🇹🇱","🇹🇲","🇹🇳","🇹🇴","🇹🇷","🇹🇹","🇹🇻","🇹🇼","🇹🇿","🇺🇦","🇺🇬","🇺🇲","🇺🇳","🇺🇸","🇺🇾","🇺🇿","🇻🇦","🇻🇨","🇻🇪","🇻🇬","🇻🇮","🇻🇳","🇻🇺","🇼🇫","🇼🇸","🇽🇰","🇾🇪","🇾🇹","🇿🇦","🇿🇲","🇿🇼","🏴󠁧󠁢󠁥󠁮󠁧󠁿","🏴󠁧󠁢󠁳󠁣󠁴󠁿","🏴󠁧󠁢󠁷󠁬󠁳󠁿","🇦","🇧","🇨","🇩","🇪","🇫","🇬","🇭","🇮","🇯","🇰","🇱","🇲","🇳","🇴","🇵","🇶","🇷","🇸","🇹","🇺","🇻","🇼","🇽","🇾","🇿"]
