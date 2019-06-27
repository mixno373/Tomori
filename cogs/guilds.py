import discord
import asyncio
import requests
import time
from datetime import datetime, date
import string
import random
import copy
import os
import re
import json
import asyncpg
from discord.ext import commands
from cogs.const import *
from cogs.util import *
from cogs.ids import *
from cogs.locale import *
from config.constants import *


async def g_guild(client, conn, context, category, arg1, args):
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
    if not const["is_global"]:
        stats_type = message.server.id
    else:
        stats_type = "global"
    em = discord.Embed(colour=int(const["em_color"], 16) + 512)
    try:
        await client.delete_message(message)
    except:
        pass


    if category == "create":
        if not arg1:
            em.description = locale[lang]["missed_argument"].format(
                who=message.author.display_name+"#"+message.author.discriminator,
                arg="name"
            )
            await client.send_message(message.channel, embed=em)
            return
        if args:
            arg1 += " "+args
        arg1 = clear_name(arg1)
        if not arg1:
            em.description = locale[lang]["incorrect_argument"].format(
                who=message.author.display_name+"#"+message.author.discriminator,
                arg="name"
            )
            await client.send_message(message.channel, embed=em)
            return
        data = await conn.fetchrow("SELECT * FROM guilds WHERE server_id = '{server}' AND stats_type = '{stats_type}' AND name = '{name}'".format(
            server=server_id,
            stats_type=stats_type,
            name=arg1
        ))
        if not data:
            dat = await conn.fetchrow("SELECT cash, guild_id FROM users WHERE stats_type = '{stats_type}' AND discord_id = '{id}'".format(stats_type=stats_type, id=message.author.id))
            if dat:
                if (const["guild_price"] > dat["cash"]):
                    em.description =  locale[lang]["global_dont_have_that_much_money"].format(who=message.author.display_name+"#"+message.author.discriminator, money=const["server_money"])
                    if not message.server.id in servers_without_follow_us:
                        em = await add_follow_links(client, message, const, em)
                else:
                    if dat["guild_id"] != 0:
                        data = await conn.fetchrow("SELECT * FROM guilds WHERE server_id = '{server}' AND stats_type = '{stats_type}' AND id = {id}".format(
                            server=server_id,
                            stats_type=stats_type,
                            id=dat["guild_id"]
                        ))
                        if data:
                            em.description = locale[lang]["guild_create_already_in_guild"].format(
                                who=message.author.display_name+"#"+message.author.discriminator,
                                name=data["name"]
                            )
                        else:
                            em.description = locale[lang]["error_with_code"].format(
                                who=message.author.display_name+"#"+message.author.discriminator,
                                code=errors.get("user_in_not_exists_guild")
                            )
                    else:
                        guild_dat = await conn.fetchrow("INSERT INTO guilds(name, owner_id, stats_type, server_id) VALUES('{name}', '{owner_id}', '{stats_type}', '{server_id}') RETURNING id".format(
                            name=arg1,
                            owner_id=message.author.id,
                            stats_type=stats_type,
                            server_id=message.server.id
                        ))
                        await conn.execute("UPDATE users SET cash = {cash}, guild_id = {guild}, guild_role = '{role}', guild_join = {time} WHERE stats_type = '{stats_type}' AND discord_id = '{id}'".format(
                            stats_type=stats_type,
                            cash=dat["cash"] - const["guild_price"],
                            guild=guild_dat["id"],
                            role="owner",
                            time=int(time.time()),
                            id=message.author.id
                        ))
                        em.description = locale[lang]["guild_create_success"].format(
                            who=message.author.display_name+"#"+message.author.discriminator,
                            name=arg1
                        )
            else:
                await conn.execute("INSERT INTO users(name, discord_id, stats_type) VALUES('{}', '{}', '{}')".format(clear_name(message.author.display_name[:50]), message.author.id, stats_type))
                em.description = locale[lang]["global_dont_have_that_much_money"].format(who=message.author.display_name+"#"+message.author.discriminator, money=const["server_money"])
                if not message.server.id in servers_without_follow_us:
                    em = await add_follow_links(client, message, const, em)
        else:
            em.description = locale[lang]["guild_create_exists"].format(
                who=message.author.display_name+"#"+message.author.discriminator,
                name=arg1
            )
        await client.send_message(message.channel, embed=em)
        return


    elif category == "delete":
        dat = await conn.fetchrow("SELECT guild_id, guild_role FROM users WHERE stats_type = '{stats_type}' AND discord_id = '{id}'".format(stats_type=stats_type, id=message.author.id))
        if not dat["guild_role"] or not dat["guild_role"] == "owner":
            em.description = locale[lang]["guild_you_are_not_owner"].format(who=message.author.display_name+"#"+message.author.discriminator)
        else:
            if not await check_captcha(client, conn, const, message.channel, message.author):
                return
            data = await conn.fetchrow("SELECT * FROM guilds WHERE id = {id} AND stats_type = '{stats_type}'".format(id=dat["guild_id"], stats_type=stats_type))
            await conn.execute("DELETE FROM guilds WHERE id = {id};\
            UPDATE users SET guild_id = 0, guild_role = NULL, guild_join = {time} WHERE guild_id = {id} AND stats_type = '{stats_type}'".format(
                id=dat["guild_id"],
                time=int(time.time()),
                stats_type=stats_type
            ))
            if not data:
                em.description = locale[lang]["error_with_code"].format(
                    who=message.author.display_name+"#"+message.author.discriminator,
                    code=errors.get("guild_remove_not_exists")
                )
            else:
                em.description = locale[lang]["guild_remove_success"].format(
                    who=message.author.display_name+"#"+message.author.discriminator,
                    name=data["name"]
                )
        await client.send_message(message.channel, embed=em)
        return


    elif category == "info":
        who = message.author
        if arg1:
            if args:
                arg1 += " "+args
            who = discord.utils.get(message.server.members, name=arg1)
            if not who:
                arg1 = re.sub(r'[<@#&!>]+', '', arg1.lower())
                who = discord.utils.get(message.server.members, id=arg1)
            if not who:
                who = message.author
        dat = await conn.fetchrow("SELECT guild_id, guild_role FROM users WHERE stats_type = '{stats_type}' AND discord_id = '{id}'".format(stats_type=stats_type, id=who.id))
        if dat["guild_id"] == 0 or not dat["guild_role"] or dat["guild_role"] == "waiter":
            em.description = locale[lang]["guild_are_not_member"].format(who=who.display_name+"#"+who.discriminator)
        else:
            data = await conn.fetchrow("SELECT * FROM guilds WHERE id = {id} AND stats_type = '{stats_type}'".format(id=dat["guild_id"], stats_type=stats_type))
            guild_members = await conn.fetchrow("SELECT COUNT(name) FROM users WHERE guild_id = {id} AND guild_role <> 'waiter' AND stats_type = '{stats_type}'".format(id=dat["guild_id"], stats_type=stats_type))
            if not data:
                em.description = locale[lang]["error_with_code"].format(
                    who=message.author.display_name+"#"+message.author.discriminator,
                    code=errors.get("guild_info_not_exists")
                )
            else:
                em.set_author(name=locale[lang]["guild_info_title"].format(name=data["name"]))
                icon_url = data["icon_url"]
                if icon_url:
                    try:
                        response = str(requests.session().get(icon_url).content)
                        if not response[2:-1]:
                            icon_url = None
                    except:
                        icon_url = None
                if not icon_url:
                    icon_url = message.author.default_avatar_url
                em.set_thumbnail(url=icon_url)
                owner = message.server.get_member(data["owner_id"])
                if not owner:
                    owner = client.user
                is_private = locale[lang]["no"]
                if data["is_private"]:
                    is_private = locale[lang]["yes"]
                try:
                    percent = int(100*data["win_count"]/(data["win_count"]+data["lose_count"]))
                except:
                    percent = 0
                em.add_field(
                    name=locale[lang]["guild_owner"],
                    value="{0.name}#{0.discriminator}".format(owner),
                    inline=True
                )
                em.add_field(
                    name=locale[lang]["guild_members"],
                    value=str(guild_members[0]),
                    inline=True
                )
                em.add_field(
                    name=locale[lang]["guild_winrate"],
                    value=locale[lang]["guild_winrate_value"].format(
                        win=data["win_count"],
                        all=data["win_count"]+data["lose_count"],
                        percent=percent
                    ),
                    inline=True
                )
                em.add_field(
                    name=locale[lang]["guild_xp_count"],
                    value=str(data["xp_count"]),
                    inline=True
                )
                em.add_field(
                    name=locale[lang]["guild_bank"],
                    value=str(data["cash"]),
                    inline=True
                )
                em.add_field(
                    name=locale[lang]["guild_private"],
                    value=is_private,
                    inline=True
                )
                em.set_footer(text=who.display_name+"#"+who.discriminator)
        await client.send_message(message.channel, embed=em)
        return


    elif category == "join":
        if not arg1:
            em.description = locale[lang]["missed_argument"].format(
                who=message.author.display_name+"#"+message.author.discriminator,
                arg="name"
            )
            await client.send_message(message.channel, embed=em)
            return
        if args:
            arg1 += " "+args
        arg1 = clear_name(arg1)
        if not arg1:
            em.description = locale[lang]["incorrect_argument"].format(
                who=message.author.display_name+"#"+message.author.discriminator,
                arg="name"
            )
            await client.send_message(message.channel, embed=em)
            return
        dat = await conn.fetchrow("SELECT * FROM users WHERE stats_type = '{stats_type}' AND discord_id = '{id}'".format(stats_type=stats_type, id=message.author.id))
        if not dat:
            em.description = locale[lang]["error_with_code"].format(
                who=message.author.display_name+"#"+message.author.discriminator,
                code=errors.get("guild_join_member_not_exists")
            )
            await client.send_message(message.channel, embed=em)
            return
        elif not dat["guild_id"] == 0 or (dat["guild_role"] and not dat["guild_role"] == "waiter"):
            em.description = locale[lang]["guild_join_already_in_guild"].format(who=message.author.display_name+"#"+message.author.discriminator)
            await client.send_message(message.channel, embed=em)
            return
        data = await conn.fetchrow("SELECT * FROM guilds WHERE stats_type = '{stats_type}' AND name = '{name}'".format(stats_type=stats_type, name=arg1))
        if not data:
            em.description = locale[lang]["guild_not_exists"].format(
                who=message.author.display_name+"#"+message.author.discriminator,
                name=arg1
            )
        else:
            guild_role = "member"
            if data["is_private"]:
                guild_role = "waiter"
            await conn.execute("UPDATE users SET guild_id = {guild_id}, guild_role = '{guild_role}', guild_join = {time} WHERE discord_id = '{discord_id}' AND stats_type = '{stats_type}'".format(
                guild_id=data["id"],
                guild_role=guild_role,
                time=int(time.time()),
                discord_id=message.author.id,
                stats_type=stats_type
            ))
            if guild_role == 'member':
                em.description = locale[lang]["guild_join_member_success"].format(
                    who=message.author.display_name+"#"+message.author.discriminator,
                    name=data["name"]
                )
            else:
                em.description = locale[lang]["guild_join_waiter_success"].format(
                    who=message.author.display_name+"#"+message.author.discriminator,
                    name=data["name"]
                )
        await client.send_message(message.channel, embed=em)
        return
    #
    # elif category == "set":
    #     if not arg1:
    #         em.description = locale[lang]["missed_argument"].format(
    #             who=message.author.display_name+"#"+message.author.discriminator,
    #             arg="type"
    #         )
    #         await client.send_message(message.channel, embed=em)
    #         return
    #
    #     if arg1 == "icon":
    #     if not arg1:
    #         em.description = locale[lang]["incorrect_argument"].format(
    #             who=message.author.display_name+"#"+message.author.discriminator,
    #             arg="name"
    #         )
    #         await client.send_message(message.channel, embed=em)
    #         return
    #     dat = await conn.fetchrow("SELECT * FROM users WHERE stats_type = '{stats_type}' AND discord_id = '{id}'".format(stats_type=stats_type, id=message.author.id))
    #     if not dat:
    #         em.description = locale[lang]["error_with_code"].format(
    #             who=message.author.display_name+"#"+message.author.discriminator,
    #             code=errors.get("guild_join_member_not_exists")
    #         )
    #         await client.send_message(message.channel, embed=em)
    #         return
    #     elif not dat["guild_id"] == 0 or (dat["guild_role"] and not dat["guild_role"] == "waiter"):
    #         em.description = locale[lang]["guild_join_already_in_guild"].format(who=message.author.display_name+"#"+message.author.discriminator)
    #         await client.send_message(message.channel, embed=em)
    #         return
    #     data = await conn.fetchrow("SELECT * FROM guilds WHERE stats_type = '{stats_type}' AND name = '{name}'".format(stats_type=stats_type, name=arg1))
    #     if not data:
    #         em.description = locale[lang]["guild_not_exists"].format(
    #             who=message.author.display_name+"#"+message.author.discriminator,
    #             name=arg1
    #         )
    #     else:
    #         guild_role = "member"
    #         if data["is_private"]:
    #             guild_role = "waiter"
    #         await conn.execute("UPDATE users SET guild_id = {guild_id}, guild_role = '{guild_role}', guild_join = {time} WHERE discord_id = '{discord_id}' AND stats_type = '{stats_type}'".format(
    #             guild_id=data["id"],
    #             guild_role=guild_role,
    #             time=int(time.time()),
    #             discord_id=message.author.id,
    #             stats_type=stats_type
    #         ))
    #         if guild_role == 'member':
    #             em.description = locale[lang]["guild_join_member_success"].format(
    #                 who=message.author.display_name+"#"+message.author.discriminator,
    #                 name=data["name"]
    #             )
    #         else:
    #             em.description = locale[lang]["guild_join_waiter_success"].format(
    #                 who=message.author.display_name+"#"+message.author.discriminator,
    #                 name=data["name"]
    #             )
    #     await client.send_message(message.channel, embed=em)
    #     return


    elif category == "list":
        page = 1
        if arg1:
            if args:
                arg1 += " "+args
            try:
                page = int(arg1)
                if page < 1:
                    page = 1
            except:
                pass
        dat = await conn.fetchrow("SELECT guild_id, guild_role FROM users WHERE stats_type = '{stats_type}' AND discord_id = '{id}'".format(stats_type=stats_type, id=message.author.id))
        if not dat["guild_role"] or not dat["guild_role"] == "owner":
            em.description = locale[lang]["guild_you_are_not_owner"].format(who=message.author.display_name+"#"+message.author.discriminator)
            await client.send_message(message.channel, embed=em)
            return
        data = await conn.fetchrow("SELECT COUNT(name) FROM users WHERE  guild_id = {id} AND guild_role = 'waiter' AND stats_type = '{stats_type}'".format(id=dat["guild_id"], stats_type=stats_type))
        all_count = data[0]
        pages = (((all_count - 1) // 25) + 1)
        em.title = locale[lang]["guild_list_title"]
        if all_count == 0:
            em.description = locale[lang]["global_list_is_empty"]
            await client.send_message(message.channel, embed=em)
            return
        if page > pages:
            em.description = locale[lang]["global_page_not_exists"].format(who=message.author.display_name+"#"+message.author.discriminator, number=page)
            await client.send_message(message.channel, embed=em)
            return
        data = await conn.fetch("SELECT * FROM  users WHERE guild_id = {id} AND guild_role = 'waiter' AND stats_type = '{stats_type}' ORDER BY guild_join ASC LIMIT 25 OFFSET {offset}".format(id=dat["guild_id"], stats_type=stats_type, offset=(page-1)*25))
        if data:
            for index, dat_user in enumerate(data):
                user = discord.utils.get(message.server.members, id=dat_user["discord_id"])
                if user:
                    mention = user.mention
                else:
                    mention = "Unknown User"
                em.add_field(
                    name="󠂪",
                    value="**#{index} {name}**".format(index=index+1+(page-1)*25, name=mention),
                    inline=True
                )
            em.set_footer(text=locale[lang]["other_footer_page"].format(number=page, length=pages))
        else:
            em.description = locale[lang]["global_list_is_empty"]
        await client.send_message(message.channel, embed=em)
        return


    elif category == "accept":
        if not arg1:
            em.description = locale[lang]["missed_argument"].format(
                who=message.author.display_name+"#"+message.author.discriminator,
                arg="name"
            )
            await client.send_message(message.channel, embed=em)
            return
        if args:
            arg1 += " "+args
        who = discord.utils.get(message.server.members, name=arg1)
        if not who:
            arg1 = re.sub(r'[<@#&!>]+', '', arg1.lower())
            who = discord.utils.get(message.server.members, id=arg1)
        dat = await conn.fetchrow("SELECT guild_id, guild_role FROM users WHERE stats_type = '{stats_type}' AND discord_id = '{id}'".format(stats_type=stats_type, id=message.author.id))
        if not dat["guild_role"] or not dat["guild_role"] == "owner":
            em.description = locale[lang]["guild_you_are_not_owner"].format(who=message.author.display_name+"#"+message.author.discriminator)
            await client.send_message(message.channel, embed=em)
            return
        if arg1.isdigit() and not arg1 == "0" or arg1 == "all":
            if arg1 == "all":
                select = "SELECT * FROM users WHERE guild_id = {id} AND guild_role = 'waiter' AND stats_type = '{stats_type}' ORDER BY guild_join ASC".format(id=dat["guild_id"], stats_type=stats_type)
            else:
                select = "SELECT * FROM users WHERE guild_id = {id} AND guild_role = 'waiter' AND stats_type = '{stats_type}' ORDER BY guild_join ASC LIMIT 1 OFFSET {offset}".format(id=dat["guild_id"], stats_type=stats_type, offset=int(arg1)-1)
        elif who:
            select = "SELECT * FROM users WHERE guild_id = {id} AND guild_role = 'waiter' AND stats_type = '{stats_type}' AND discord_id = '{discord_id}'".format(id=dat["guild_id"], stats_type=stats_type, discord_id=who.id)
        else:
            em.description = locale[lang]["incorrect_argument"].format(
                who=message.author.display_name+"#"+message.author.discriminator,
                arg="number"
            )
            await client.send_message(message.channel, embed=em)
        await conn.execute("UPDATE users SET guild_role = 'member' FROM ({select}) AS subusers WHERE users.id=subusers.id".format(select=select))
        em.description = locale[lang]["guild_accept_success"].format(who=message.author.display_name+"#"+message.author.discriminator)
        await client.send_message(message.channel, embed=em)
        return


    elif category == "cancel":
        dat = await conn.fetchrow("SELECT guild_id, guild_role FROM users WHERE stats_type = '{stats_type}' AND discord_id = '{id}'".format(stats_type=stats_type, id=message.author.id))
        if dat["guild_role"] and dat["guild_role"] == "waiter":
            await conn.execute("UPDATE users SET guild_id = 0, guild_role = NULL, guild_join = {time} WHERE stats_type = '{stats_type}' AND discord_id = '{id}'".format(time=int(time.time()), stats_type=stats_type, id=message.author.id))
            em.description = locale[lang]["guild_cancel_success"].format(who=message.author.display_name+"#"+message.author.discriminator)
        elif dat["guild_role"] and dat["guild_role"] == "owner":
            if not arg1:
                em.description = locale[lang]["missed_argument"].format(
                    who=message.author.display_name+"#"+message.author.discriminator,
                    arg="name"
                )
                await client.send_message(message.channel, embed=em)
                return
            if args:
                arg1 += " "+args
            who = discord.utils.get(message.server.members, name=arg1)
            if not who:
                arg1 = re.sub(r'[<@#&!>]+', '', arg1.lower())
                who = discord.utils.get(message.server.members, id=arg1)
            if arg1.isdigit() and not arg1 == "0" or arg1 == "all":
                if arg1 == "all":
                    select = "SELECT * FROM users WHERE guild_id = {id} AND guild_role = 'waiter' AND stats_type = '{stats_type}' ORDER BY guild_join ASC".format(id=dat["guild_id"], stats_type=stats_type)
                else:
                    select = "SELECT * FROM users WHERE guild_id = {id} AND guild_role = 'waiter' AND stats_type = '{stats_type}' ORDER BY guild_join ASC LIMIT 1 OFFSET {offset}".format(id=dat["guild_id"], stats_type=stats_type, offset=int(arg1)-1)
            elif who:
                select = "SELECT * FROM users WHERE guild_id = {id} AND guild_role = 'waiter' AND stats_type = '{stats_type}' AND discord_id = '{discord_id}'".format(id=dat["guild_id"], stats_type=stats_type, discord_id=who.id)
            else:
                em.description = locale[lang]["incorrect_argument"].format(
                    who=message.author.display_name+"#"+message.author.discriminator,
                    arg="number"
                )
                await client.send_message(message.channel, embed=em)
            await conn.execute("UPDATE users SET guild_id = 0, guild_role = NULL, guild_join = {time} FROM ({select}) AS subusers WHERE users.id=subusers.id".format(time=int(time.time()), select=select))
            em.description = locale[lang]["guild_cancel_success"].format(who=message.author.display_name+"#"+message.author.discriminator)
        elif dat["guild_role"]:
            em.description = locale[lang]["guild_you_are_not_owner"].format(who=message.author.display_name+"#"+message.author.discriminator)
        else:
            em.description = locale[lang]["guild_are_not_member"].format(who=message.author.display_name+"#"+message.author.discriminator)
        await client.send_message(message.channel, embed=em)
        return


    elif category == "leave":
        dat = await conn.fetchrow("SELECT guild_id, guild_role FROM users WHERE stats_type = '{stats_type}' AND discord_id = '{id}'".format(stats_type=stats_type, id=message.author.id))
        if dat["guild_role"] and dat["guild_role"] == "owner":
            em.description = locale[lang]["guild_cant_leave_cause_owner"].format(who=message.author.display_name+"#"+message.author.discriminator)
            await client.send_message(message.channel, embed=em)
            return
        elif not dat["guild_role"] or not dat["guild_role"] == "member":
            em.description = locale[lang]["guild_are_not_member"].format(who=message.author.display_name+"#"+message.author.discriminator)
        else:
            if not await check_captcha(client, conn, const, message.channel, message.author):
                return
            await conn.execute("UPDATE users SET guild_id = 0, guild_role = NULL, guild_join = {time} WHERE stats_type = '{stats_type}' AND discord_id = '{id}'".format(time=int(time.time()), stats_type=stats_type, id=message.author.id))
            em.description = locale[lang]["guild_leave_success"].format(who=message.author.display_name+"#"+message.author.discriminator)
        await client.send_message(message.channel, embed=em)
        return


    else:
        em.description = locale[lang]["incorrect_argument"].format(
            who=message.author.display_name+"#"+message.author.discriminator,
            arg="category"
        )
        await client.send_message(message.channel, embed=em)
