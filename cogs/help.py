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
from cogs.const import *
from config.constants import *

help_responses = {
    "english" : {
        "command" : "Command `{command}`",
        "usage" : "**Usage:**\n",
        "command_not_found" : "Command not found!",
        "help" : {
            "description" : "Show command list",
            "usage" : "`{prefix}help` - command list\n`{prefix}help <command>` - show info about __command__",
            "rights" : ""
        },
        "set" : {
            "description" : "Change server settings",
            "usage" : "`{prefix}set [category]`\n" + \
                "Also you can write `{prefix}set list` for a list of settings\n" + \
                    "All possible settings you can see on the [website](https://discord.band/commands#/ADMIN)",
            "list_desctiption" : "List of settings",
            "rights" : "\n\n**Rights:**\nNeed permissions __**Administrator**__"
        },
        "timely" : {
            "description" : "Get __money__ [500 {money} every 12 hours]",
            "usage" : "`{prefix}timely`",
            "rights" : ""
        },
        "work" : {
            "description" : "Go to a work [50 {money} every 30 minutes]",
            "usage" : "`{prefix}work`",
            "rights" : ""
        },
        "server" : {
            "description" : "Show information about this server",
            "usage" : "`{prefix}server`",
            "rights" : ""
        },
        "ping" : {
            "description" : "Check ping to Tomori",
            "usage" : "`{prefix}ping`",
            "rights" : ""
        },
        "buy" : {
            "description" : "Buy a role from shop",
            "usage" : "`{prefix}buy [name|mention|id|number in a list]`",
            "rights" : ""
        },
        "shop" : {
            "description" : "Show list of roles in the shop",
            "usage" : "`{prefix}shop`\n`{prefix}shop [page]`",
            "rights" : ""
        },
        "pay" : {
            "description" : "Take __money__ from server bank",
            "usage" : "`{prefix}pay <count>`",
            "rights" : "\n\n**Rights:**\nNeed permissions __**Owner**__"
        },
        "send" : {
            "description" : "Send file from this __url__ by Tomori",
            "usage" : "`{prefix}send` <url>",
            "rights" : "\n\n**Rights:**\nNeed permissions __**Administrator**__"
        },
        "say" : {
            "description" : "Send __text__ by Tomori",
            "usage" : "`{prefix}say <text>`\n`{prefix}say [channel] <text>`",
            "rights" : "\n\n**Rights:**\nNeed permissions __**Administrator**__"
        },
        "report" : {
            "description" : "Send a report to Tomori developers",
            "usage" : "`{prefix}report [text]`",
            "rights" : ""
        },
        "give" : {
            "description" : "Give your {money} to somebody",
            "usage" : "`{prefix}give <@who> <count>`",
            "rights" : ""
        },
        "top" : {
            "description" : "Show top users by XP",
            "usage" : "`{prefix}top [page]`",
            "rights" : ""
        },
        "remove" : {
            "description" : "Reset some settings",
            "usage" : "`{prefix}remove <category> [name]`",
            "aliases": "rm",
            "rights" : "\n\n**Rights:**\nNeed permissions __**Administrator**__"
        },
        "rm" : {
            "description" : "Reset some settings",
            "usage" : "`{prefix}remove <category> [name]`",
            "aliases": "rm",
            "rights" : "\n\n**Rights:**\nNeed permissions __**Administrator**__"
        },
        "backgrounds" : {
            "description" : "Show a list of backgrounds",
            "usage" : "`{prefix}backgrounds [page]`",
            "aliases": "backs",
            "rights" : ""
        },
        "backs" : {
            "description" : "Show a list of backgrounds",
            "usage" : "`{prefix}backgrounds [page]`",
            "aliases": "backs",
            "rights" : ""
        },
        "$" : {
            "description" : "Show your balance",
            "usage" : "`{prefix}$`",
            "rights" : ""
        },
        "hug" : {
            "description" : "Hug somebody [30 {money}]",
            "usage" : "`{prefix}hug <@who>`",
            "rights" : ""
        },
        "wink" : {
            "description" : "Wink to somebody [20 {money}]",
            "usage" : "`{prefix}wink <@who>`",
            "rights" : ""
        },
        "five" : {
            "description" : "High-five somebody [5 {money}]",
            "usage" : "`{prefix}five <@who>`",
            "rights" : ""
        },
        "fuck" : {
            "description" : "Fuck somebody [15 {money}]",
            "usage" : "`{prefix}fuck <@who>`",
            "rights" : ""
        },
        "punch" : {
            "description" : "Punch somebody [20 {money}]",
            "usage" : "`{prefix}punch <@who>`",
            "rights" : ""
        },
        "kiss" : {
            "description" : "Kiss somebody [30 {money}]",
            "usage" : "`{prefix}kiss <@who>`",
            "rights" : ""
        },
        "drink" : {
            "description" : "Drink some alchogol [45 {money}]",
            "usage" : "`{prefix}drink <@who>`",
            "rights" : ""
        },
        "shiki" : {
            "description" : "Find anime at Shikimori",
            "usage" : "`{prefix}shiki <name>`",
            "rights" : ""
        },
        "br" : {
            "description" : "Play a bet-roll",
            "usage" : "`{prefix}br <bet>`",
            "aliases": "roll",
            "rights" : ""
        },
        "roll" : {
            "description" : "Play a bet-roll",
            "usage" : "`{prefix}br <bet>`",
            "aliases": "roll",
            "rights" : ""
        },
        "slots" : {
            "description" : "Play a slot-machine",
            "usage" : "`{prefix}slots <bet>`",
            "aliases": "slot",
            "rights" : ""
        },
        "slot" : {
            "description" : "Play a slot-machine",
            "usage" : "`{prefix}slots <bet>`",
            "aliases": "slot",
            "rights" : ""
        },
        "rep" : {
            "description" : "Give reputation to somebody",
            "usage" : "`{prefix}rep <@who>`",
            "rights" : ""
        },
        "avatar" : {
            "description" : "Show users avatar",
            "usage" : "`{prefix}avatar <@who>`",
            "rights" : ""
        },
        "me" : {
            "description" : "Show users profile",
            "usage" : "`{prefix}me [@who]`",
            "aliases": "profile",
            "rights" : ""
        },
        "profile" : {
            "description" : "Show users profile",
            "usage" : "`{prefix}me [@who]`",
            "aliases": "profile",
            "rights" : ""
        },
        "about" : {
            "description" : "Show information about Tomori",
            "usage" : "`{prefix}about`",
            "rights" : ""
        },
        "invite" : {
            "description" : "Get Tomori invite link",
            "usage" : "`{prefix}invite`",
            "rights" : ""
        },
        "clear" : {
            "description" : "Remove <count> messages from channel",
            "usage" : "`{prefix}clear <count`",
            "aliases": "cl",
            "rights" : "\n\n**Rights:**\nNeed permissions __**Administrator**__ or __**Manage messages**__"
        },
        "cl" : {
            "description" : "Remove <count> messages from channel",
            "usage" : "`{prefix}clear <count`",
            "aliases": "cl",
            "rights" : "\n\n**Rights:**\nNeed permissions __**Administrator**__ or __**Manage messages**__"
        },
        "kick" : {
            "description" : "Kick user",
            "usage" : "`{prefix}kick <@who>`",
            "rights" : "\n\n**Rights:**\nNeed permissions __**Administrator**__ or __**Kick members**__"
        },
        "ban" : {
            "description" : "Ban user",
            "usage" : "`{prefix}ban <@who>`",
            "rights" : "\n\n**Rights:**\nNeed permissions __**Administrator**__ or __**Ban members**__"
        },
        "unban" : {
            "description" : "Unban user",
            "usage" : "`{prefix}unban <@who>`",
            "rights" : "\n\n**Rights:**\nNeed permissions __**Administrator**__ or __**Ban members**__"
        }
    },
    "russian" : {
        "command" : "Команда `{command}`",
        "usage" : "**Использование:**\n",
        "command_not_found" : "Команда не найдена!",
        "help" : {
            "description" : "Показать список команд",
            "usage" : "`{prefix}help` - список команд\n`{prefix}help <команда>` - выводит информацию о __команде__",
            "rights" : ""
        },
        "set" : {
            "description" : "Изменить настройки сервера",
            "usage" : "`{prefix}set <category>`\n" + \
                "Также вы можете получить весь список настроек с помощью команды `{prefix}help set list`",
            "list_desctiption" : "Список настроек",
            "rights" : "\n\n**Rights:**\nНужны права __**Администратор**__"
        },
        "timely" : {
            "description" : "Cобрать валюту [500 {money} каждые 12 часов]",
            "usage" : "`{prefix}timely` - получить ежедневную выплату",
            "rights" : ""
        },
        "work" : {
            "description" : "Выйти на работу [50 {money} каждые 30 минут]",
            "usage" : "`{prefix}work`",
            "rights" : ""
        },
        "server" : {
            "description" : "Показать информацию о сервере",
            "usage" : "`{prefix}server`",
            "rights" : ""
        },
        "ping" : {
            "description" : "Проверить задержку соединения",
            "usage" : "`{prefix}ping`",
            "rights" : ""
        },
        "buy" : {
            "description" : "Купить роль",
            "usage" : "`{prefix}buy <имя|id|линк|номер в магазине>`",
            "rights" : ""
        },
        "shop" : {
            "description" : "Показать магазин ролей",
            "usage" : "`{prefix}shop`\n`{prefix}shop [страница]`",
            "rights" : ""
        },
        "pay" : {
            "description" : "Получить {money} из банка сервера",
            "usage" : "`{prefix}pay <кол-во>`",
            "rights" : "\n\n**Rights:**\nНужны права __**Администратор**__"
        },
        "send" : {
            "description" : "Скачать __файл__ по __ссылке__ и отправить от имени бота",
            "usage" : "Отправить `{prefix}send` <ссылка>",
            "rights" : "\n\n**Rights:**\nНужны права __**Администратор**__"
        },
        "say" : {
            "description" : "Напишет __текст__ от имени бота",
            "usage" : "`{prefix}say <текст>`\n`{prefix}say [чат] <текст>`",
            "rights" : "\n\n**Rights:**\nНужны права __**Администратор**__"
        },
        "report" : {
            "description" : "Отправить репорт",
            "usage" : "`{prefix}report <текст>`",
            "rights" : ""
        },
        "give" : {
            "description" : "Передать свои {money}",
            "usage" : "`{prefix}give <@кто> <кол-во>`",
            "rights" : ""
        },
        "top" : {
            "description" : "Показать топ пользователей по опыту",
            "usage" : "`{prefix}top`\n`{prefix}top [страница]`",
            "rights" : ""
        },
        "remove" : {
            "description" : "Сбросить настройкe",
            "usage" : "`{prefix}remove <категория> [название]`",
            "aliases": "rm",
            "rights" : "\n\n**Rights:**\nНужны права __**Администратор**__"
        },
        "rm" : {
            "description" : "Сбросить настройкe",
            "usage" : "`{prefix}remove <категория> [название]`",
            "aliases": "rm",
            "rights" : "\n\n**Rights:**\nНужны права __**Администратор**__"
        },
        "backgrounds" : {
            "description" : "Показать список фонов",
            "usage" : "`{prefix}backgrounds`\n`{prefix}backs`\n`{prefix}backgrounds [страница]`",
            "aliases": "backs",
            "rights" : ""
        },
        "backs" : {
            "description" : "Показать список фонов",
            "usage" : "`{prefix}backgrounds`\n`{prefix}backs`\n`{prefix}backgrounds [страница]`",
            "aliases": "backs",
            "rights" : ""
        },
        "$" : {
            "description" : "Посмотреть свой баланс",
            "usage" : "`{prefix}$`",
            "rights" : ""
        },
        "hug" : {
            "description" : "Обнять [30 {money}]",
            "usage" : "`{prefix}hug <@кто>`",
            "rights" : ""
        },
        "wink" : {
            "description" : "Подмигнуть [20 {money}]",
            "usage" : "`{prefix}wink <@кто>`",
            "rights" : ""
        },
        "five" : {
            "description" : "Дать пять [5 {money}]",
            "usage" : "`{prefix}five <@кто>`",
            "rights" : ""
        },
        "fuck" : {
            "description" : "Показать фак [15 {money}]",
            "usage" : "`{prefix}fuck <@кто>`",
            "rights" : ""
        },
        "punch" : {
            "description" : "Дать леща [20 {money}]",
            "usage" : "`{prefix}punch <@кто>`",
            "rights" : ""
        },
        "kiss" : {
            "description" : "Поцеловать [30 {money}]",
            "usage" : "`{prefix}kiss <@кто>`",
            "rights" : ""
        },
        "drink" : {
            "description" : "Уйти в запой [45 {money}]",
            "usage" : "`{prefix}drink <@кто>`",
            "rights" : ""
        },
        "shiki" : {
            "description" : "Найти аниме на Shikimori",
            "usage" : "`{prefix}shiki <название>`",
            "rights" : ""
        },
        "br" : {
            "description" : "Поставить {money} на рулетке",
            "usage" : "`{prefix}br <ставка>`",
            "aliases": "roll",
            "rights" : ""
        },
        "roll" : {
            "description" : "Поставить {money} на рулетке",
            "usage" : "`{prefix}br <ставка>`",
            "aliases": "roll",
            "rights" : ""
        },
        "slots" : {
            "description" : "Поставить {money} на рулетке",
            "usage" : "`{prefix}slots <ставка>`",
            "aliases": "slot",
            "rights" : ""
        },
        "slot" : {
            "description" : "Поставить {money} на рулетке",
            "usage" : "`{prefix}slots <ставка>`",
            "aliases": "slot",
            "rights" : ""
        },
        "rep" : {
            "description" : "Выразить свое почтение",
            "usage" : "`{prefix}rep <@кто>`",
            "rights" : ""
        },
        "avatar" : {
            "description" : "Показать аватар пользователя",
            "usage" : "`{prefix}avatar <@кто>`",
            "rights" : ""
        },
        "me" : {
            "description" : "Показать профиль пользователя",
            "usage" : "`{prefix}me <@кто>`",
            "aliases": "profile",
            "rights" : ""
        },
        "about" : {
            "description" : "Показать информацию о Tomori",
            "usage" : "`{prefix}about`",
            "rights" : ""
        },
        "invite" : {
            "description" : "Получить ссылку на добавление Tomori себе на сервер",
            "usage" : "`{prefix}invite`",
            "rights" : ""
        },
        "clear" : {
            "description" : "Удалить последние сообщения",
            "usage" : "`{prefix}clear <кол-во>`",
            "aliases": "cl",
            "rights" : "\n\n**Rights:**\nНужны права __**Администратор**__ или __**Управление сообщениями**__"
        },
        "cl" : {
            "description" : "Удалить последние сообщения",
            "usage" : "`{prefix}clear <кол-во>`",
            "aliases": "cl",
            "rights" : "\n\n**Rights:**\nНужны права __**Администратор**__ или __**Управление сообщениями**__"
        },
        "kick" : {
            "description" : "Кикнуть пользователя",
            "usage" : "`{prefix}kick <@кто>`",
            "rights" : "\n\n**Rights:**\nНужны права __**Администратор**__ или __**Выгнать участников**__"
        },
        "ban" : {
            "description" : "Забанить пользователя",
            "usage" : "`{prefix}ban <@кто>`",
            "rights" : "\n\n**Rights:**\nНужны права __**Администратор**__ или __**Банить участников**__"
        },
        "unban" : {
            "description" : "Разбанить пользователя",
            "usage" : "`{prefix}unban <@кто>`",
            "rights" : "\n\n**Rights:**\nНужны права __**Администратор**__ или __**Банить участников**__"
        },
        "guild create" : {
            "description" : "Создать гильдию [{guild_price} {money}]",
            "usage" : "`{prefix}guild create <имя>`",
            "rights" : ""
        },
        "guild delete" : {
            "description" : "Удалить гильдию",
            "usage" : "`{prefix}guild delete`",
            "rights" : "\n\n**Rights:**\nНужны права __**Владелец гильдии**__"
        },
        "guild info" : {
            "description" : "Показать профиль гильдии",
            "usage" : "`{prefix}guild info\n{prefix}guild info <@кто>`",
            "rights" : ""
        },
        "guild join" : {
            "description" : "Вступить в гильдию",
            "usage" : "`{prefix}guild join <имя>`",
            "rights" : ""
        },
        "guild list" : {
            "description" : "Показать заявки в гильдию",
            "usage" : "`{prefix}guild list <страница>`",
            "rights" : "\n\n**Rights:**\nНужны права __**Владелец гильдии**__"
        },
        "guild accept" : {
            "description" : "Принять заявки в гильдию",
            "usage" : "`{prefix}guild accept <имя|id|линк|номер в списке|all>`",
            "rights" : "\n\n**Rights:**\nНужны права __**Владелец гильдии**__"
        },
        "guild cancel" : {
            "description" : "Отклонить заявки в гильдию (для владельца) или отменить заявку в гильдию (для участника)",
            "usage" : "`{prefix}guild cancel\n{prefix}guild cancel <имя|id|линк|номер в списке|all>`",
            "rights" : "\n\n**Rights:**\nНужны права __**Владелец гильдии**__ для отмены заявок в свою гильдию"
        },
        "guild leave" : {
            "description" : "Выйти из гильдии",
            "usage" : "`{prefix}guild leave`",
            "rights" : ""
        }
    }
}

supported_prefixes = ('`!','?','$','t!','t?','t$','.','-','+','\\',';','>','<','~','^','=','_`')
sup_comma = "` `"
prep = sup_comma.join(supported_prefixes)

help_set_list = {
    "english" : {
        "__Background__" : "Change background\n**Usage:**\n`{prefix}set background <name|number>`\n**Aliaces:**\n `back`",
        "__Autorole__" : "Set an autorole to user when he logging at the server\n**Usage:**\n`{prefix}set autorole <name|id|link>`\n**Rights:**\nNeed permissions __**Administrator**__",
        "__Shop__" : "Add a role to the shop\n**Usage:**\n`{prefix}set shop <name|id|link> <cost>`\n**Rights:**\nNeed permissions __**Administrator**__",
        "__Launguage__" : "Change Tomori's language\nSupported Languages: `russian`, `english`, `ukrainian`\n**Usage:**\n `{prefix}set language <lang>`\n**Aliaces:**\n `lang`\n**Rights:**\nNeed permissions __**Administrator**__",
        "__Prefix__" : "Set Prefix\nSupported Prefixes: "+prep+"\n**Usage:**\n`{prefix}set prefix [prefix]`\n**Rights:**\nNeed permissions __**Administrator**__"
    },
    "russian" : {
        "__Background__" : "Сменить фон профиля\n**Использование:**\n`{prefix}set background <имя|номер>`\n**Aliaces:**\n `back`",
        "__Autorole__" : "Установить автороль участникам при входе на сервер\n**Использование:**\n`{prefix}set autorole <имя|id|ссылка>`\n**Rights:**\nНужны права __**Администратор**__",
        "__Shop__" : "Добавить роль в магазин\n**Usage:**\n`{prefix}set shop <имя|id|ссылка> <цена>`\n**Rights:**\nНужны права __**Администратор**__",
        "__Launguage__" : "Сменить язык\nДоступные языки: `russian, english, ukrainian`\n**Использование:**\n `{prefix}set language <язык>`\n**Aliaces:**\n `lang`\n**Rights:**\nНужны права __**Администратор**__",
        "__Prefix__" : "Сменить префикс\nДоступные префиксы:  "+prep+"\n**Использование:**\n`{prefix}set prefix <префикс>`\n**Rights:**\nНужны права __**Администратор**__"
    }
}



async def h_check_help(client, conn, message):

    server_id = message.server.id

    formatted_message = message.content.split(" ", maxsplit=1)
    command = formatted_message[1]

    const = await get_cached_server(conn, server_id)
    lang = const["locale"] if const["locale"] in help_responses.keys() else "english" #Проверка на наличие языка в словаре, иначе Английский
    prefix = const["prefix"]

    em = discord.Embed(colour=int(const["em_color"], 16) + 512)
    em.title = help_responses[lang]["command"].format(command=command)
    em.set_footer(text="{name}#{discriminator}".format(
        name=message.author.name,
        discriminator=message.author.discriminator
    ))

    if command == "set list":
        em.description = help_responses[lang]["set"]["list_desctiption"]
        if lang in help_set_list.keys():
            for c, d in help_set_list[lang].items():
                em.add_field(name=c, value=d.format(prefix = prefix), inline=False)
        else:
            em.description = help_responses["english"]["command_not_found"]
        await client.send_message(message.channel, embed=em)
        return

    try:
        aliases = help_responses[lang][command].get("aliases")
        if not aliases:
            aliases = ""
        else:
            aliases = "\n**Aliaces:**\n`" + aliases + "`"
    except:
        aliases = ""

    if command in help_responses[lang].keys():
        em.description = "{desc}\n\n{usage}{aliases}{rights}".format(
            desc=help_responses[lang][command]["description"].format(
                prefix=prefix,
                guild_price=const["guild_price"],
                money=const["server_money"]
            ),
            usage=help_responses[lang]["usage"] + \
                help_responses[lang][command]["usage"].format(
                    prefix=prefix,
                    guild_price=const["guild_price"],
                    money=const["server_money"]
                ),
            #Складываем "Usage:" и примеры использования
            aliases=aliases,
            rights=help_responses[lang][command]["rights"]
            #Если "rights" = True, то мы сообщаем что только администраторы могут использовать эту команду
            )
    else:
        em.description = help_responses[lang]["command_not_found"]

    await client.send_message(message.channel, embed=em)
    return
