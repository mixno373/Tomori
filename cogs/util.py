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
import copy
from discord.ext import commands
from cogs.locale import *
from cogs.const import *


# ADD COLUMN
# users_info->voice_channel_id
# settings->is_createvoice

global voice_clients
voice_clients = []


async def u_voice_state_update(client, conn, logger, before, after):
    ret = '---------[voice_state_update]:{0.server.name} | {0.server.id}\n'.format(before)
    if before.voice.voice_channel:
        ret += 'before - {0.name} | {0.id} -> {0.voice.voice_channel.name} | {0.voice.voice_channel.id}\n'.format(before)
    if after.voice.voice_channel:
        ret += 'after - {0.name} | {0.id} -> {0.voice.voice_channel.name} | {0.voice.voice_channel.id}\n'.format(after)
    logger.info(ret)
    if before.bot:
        return
    const = await conn.fetchrow("SELECT create_lobby_id, em_color FROM settings WHERE discord_id = '{}'".format(before.server.id))
    if not const:
        logger.error('Сервер {0.name} | {0.id} отсутствует в базе! User - {1.name} | {1.id}\n'.format(before.server, before))
        return
    if not const[0]:
        return
    em = discord.Embed(colour=int(const[1], 16) + int("0x200", 16))
    global voice_clients
    if before.voice.voice_channel and before.voice.voice_channel != after.voice.voice_channel:
        if before.id in voice_clients:
            voice_clients.pop(voice_clients.index(before.id))
        dat = await conn.fetchrow("SELECT voice_channel_id FROM users WHERE discord_id = '{0.id}'".format(before))
        if dat:
            if before.voice.voice_channel.id == dat[0]:
                await conn.execute("UPDATE users SET voice_channel_id = Null WHERE discord_id = '{0.id}'".format(before))
                try:
                    await client.delete_channel(before.voice.voice_channel)
                except:
                    logger.error('Сервер {0.name} | {0.id}. Не удалось удалить канал пользователя. User - {1.name} | {1.id}\n'.format(before.server, before))
                    em.description = '{}, не удалось удалить канал пользователя. Свяжитесь с администратором сервера.'.format(clear_name(before.display_name[:50]))
                    await client.send_message(before, embed=em)
    if after.voice.voice_channel and after.voice.voice_channel.id == const[0]:
        if before.id in voice_clients:
            return
        voice_clients.append(before.id)
        try:
            for_everyone = discord.ChannelPermissions(target=after.server.default_role, overwrite=discord.PermissionOverwrite(read_messages=True))
            for_after = discord.ChannelPermissions(target=after, overwrite=discord.PermissionOverwrite(create_instant_invite=True, manage_roles=False, read_messages=True, manage_channels=True, connect=True, speak=True, mute_members=False, deafen_members=False, use_voice_activation=True, move_members=False))
            private = await client.create_channel(after.server, "{name}".format(name=clear_name(after.display_name[:50])), for_everyone, for_after, type=discord.ChannelType.voice)
            await client.edit_channel(private, user_limit=2)
            await client.move_channel(private,  0)
            dat = await conn.fetchrow("SELECT name FROM users WHERE  discord_id = '{0.id}'".format(before))
            if dat:
                await conn.execute("UPDATE users SET voice_channel_id = '{0}' WHERE discord_id = '{1.id}'".format(private.id, before))
            else:
                await conn.execute("INSERT INTO users(name, discord_id, discriminator, voice_channel_id, background) VALUES('{}', '{}', '{}', '{}')".format(before.name, before.id, before.discriminator, private.id, random.choice(background_list)))
        except:
            logger.error('Сервер {0.name} | {0.id}. Не удалось создать канал. User - {1.name} | {1.id}\n'.format(before.server, before))
            em.description = '{}, не удалось создать канал. Свяжитесь с администратором сервера.'.format(clear_name(before.display_name[:50]))
            await client.send_message(before, embed=em)
            return
        try:
            await client.move_member(after, private)
        except:
            try:
                await client.delete_channel(private)
            except:
                logger.error('Сервер {0.name} | {0.id}. Не удалось удалить канал {1.name} | {1.id}. User - {2.name} | {1.id}\n'.format(before.server, private, before))
            logger.error('Сервер {0.name} | {0.id}. Не удалось переместить пользователя. User - {1.name} | {1.id}\n'.format(before.server, before))
            em.description = '{}, не удалось переместить Вас в Ваш канал. Свяжитесь с администратором сервера.'.format(clear_name(before.display_name[:50]))
            await client.send_message(before, embed=em)
            return

async def u_createvoice(client, conn, logger, context):
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
        await client.send_message(who, embed=em)
        return
    try:
        private = await client.create_channel(who.server, "private - {}".format(clear_name(who.display_name[:50])), type=discord.ChannelType.voice)
        await client.edit_channel_permissions(private, target=who.server.default_role, overwrite=discord.PermissionOverwrite(read_messages=False))
        await client.edit_channel_permissions(private, target=who, overwrite=discord.PermissionOverwrite(create_instant_invite=True, manage_roles=True, read_messages=True, manage_channels=True, connect=True, speak=True, mute_members=True, deafen_members=True, use_voice_activation=True, move_members=True))
        dat = await conn.fetchrow("SELECT name FROM users WHERE discord_id = '{0.id}'".format(who))
        if dat:
            await conn.execute("UPDATE users SET voice_channel_id = '{0}' WHERE discord_id = '{1.id}'".format(private.id, who))
        else:
            await conn.execute("INSERT INTO users(name, discord_id, discriminator, voice_channel_id, background) VALUES('{}', '{}', '{}', '{}')".format(who.name, who.id, who.discriminator, private.id, random.choice(background_list)))
    except:
        logger.error('Сервер {0.name} | {0.id}. Не удалось создать канал. User - {1.name} | {1.id}\n'.format(who.server, who))
        em.description = '{}, не удалось создать канал. Свяжитесь с администратором сервера.'.format(clear_name(who.display_name[:50]))
        await client.send_message(who, embed=em)
        return
    try:
        await client.move_member(who, private)
    except:
        try:
            await client.delete_channel(private)
        except:
            logger.error('Сервер {0.name} | {0.id}. Не удалось удалить канал {1.name} | {1.id}. User - {2.name} | {1.id}\n'.format(who.server, private, who))
        logger.error('Сервер {0.name} | {0.id}. Не удалось переместить пользователя. User - {1.name} | {1.id}\n'.format(who.server, who))
        em.description = '{}, не удалось переместить Вас в Ваш канал. Свяжитесь с администратором сервера.'.format(clear_name(who.display_name[:50]))
        await client.send_message(who, embed=em)
        return

async def u_setvoice(client, conn, logger, context):
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
        await conn.execute("UPDATE settings SET create_lobby_id = '{}' WHERE discord_id = '{}'".format(who.voice.voice_channel.id, server_id))
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

async def u_reaction_add(client, conn, logger, emoji, user_id, message_id):
    if message_id in reaction_mes_ids:
        server = client.get_server("377890113352630282")
        user = server.get_member(user_id)
        logger.info("add reaction | message_id - {0} | server_name - {1.name} | server_id - {1.id} | user_name - {2.name} | user_mention - {2.mention} | emoji - {3}\n".format(message_id, server, user, emoji['name']))
        roles = []
        if emoji["id"] == emoji_zverolud_id:
            for s in reaction_zverolud_ids:
                role = discord.utils.get(server.roles, id=s)
                if not role:
                    logger.info("doesn't exists role id - {id}".format(id=s))
                    continue
                roles.append(role)
        if emoji["id"] == emoji_nolife_id:
            for s in reaction_nolife_ids:
                role = discord.utils.get(server.roles, id=s)
                if not role:
                    logger.info("doesn't exists role id - {id}".format(id=s))
                    continue
                roles.append(role)
        if emoji["id"] == emoji_avanturist_id:
            for s in reaction_avanturist_ids:
                role = discord.utils.get(server.roles, id=s)
                if not role:
                    logger.info("doesn't exists role id - {id}".format(id=s))
                    continue
                roles.append(role)
        await client.add_roles(user, *roles)

async def u_reaction_remove(client, conn, logger, emoji, user_id, message_id):
    if message_id in reaction_mes_ids:
        server = client.get_server("377890113352630282")
        user = server.get_member(user_id)
        logger.info("remove reaction | message_id - {0} | server_name - {1.name} | server_id - {1.id} | user_name - {2.name} | user_mention - {2.mention} | emoji - {3}\n".format(message_id, server, user, emoji['name']))
        roles = []
        if emoji["id"] == emoji_zverolud_id or emoji["id"] == emoji_nolife_id or emoji["id"] == emoji_avanturist_id:
            for s in reaction_zverolud_ids:
                role = discord.utils.get(server.roles, id=s)
                if not role:
                    logger.info("doesn't exists role id - {id}".format(id=s))
                    continue
                roles.append(role)
        for s in reaction_nolife_ids:
            role = discord.utils.get(server.roles, id=s)
            if not role:
                logger.info("doesn't exists role id - {id}".format(id=s))
                continue
            roles.append(role)
        for s in reaction_avanturist_ids:
            role = discord.utils.get(server.roles, id=s)
            if not role:
                logger.info("doesn't exists role id - {id}".format(id=s))
                continue
            roles.append(role)
        await client.remove_roles(user, *roles)

async def u_check_message(client, conn, logger, message):
    for file in black_filename_list:
        if file.lower() in str(message.attachments).lower() or file.lower() in message.content.lower():
            logger.error("file detected (suck my dick enot) - ({})  <-> {}\n".format(file, message.attachments))
            try:
                dat = await conn.fetchrow("SELECT name FROM black_list WHERE server_id = '{}' AND discord_id = '{}'".format(message.server, message.author.id))
                if dat:
                    if not dat[0]:
                        await conn.execute("UPDATE black_list SET name = '{0.name}' WHERE discord_id = '{0.id}'".format(message.author))
                else:
                    await conn.execute("INSERT INTO black_list(name, discord_id) VALUES('{0.name}', '{0.id}')".format(message.author))
                    pass
                await client.delete_message(message)
                return True
            except:
                pass
    return False
    await u_check_ddos(client, conn, logger, member)

async def u_check_ddos(client, conn, logger, member):
    dat = await conn.fetchrow("SELECT name FROM black_list WHERE discord_id = '{}'".format(member.id))
    if dat:
        try:
            #logger.error("================================================================================\n**{2}**\n({0.name} | {0.mention}) -> [{1.name} | {1.id}]\n".format(member, member.server, time.ctime(time.time())))
            try:
                await client.send_message(client.get_channel('480689437257498628'), "**{2}**\n``({0.name} | {0.mention}) -> [{1.name} | {1.id}]``".format(member, member.server, time.ctime(time.time())))
                await client.send_message(member.server.owner, "**{1}**\n``С твоего сервера '{0.server.name}' кикнут ({0.name} | {0.mention}) по причине нахождения в черном списке (DDOS-атаки) Tomori.``".format(member, time.ctime(time.time())))
                await client.send_message(member, "**{1}**\n``Вас кикнули с сервера '{0.server.name}' по причине нахождения в черном списке (DDOS-атаки) Tomori. По вопросам разбана писать Ананасовая Печенюха [Cookie]#0001 (<@>282660110545846272)``".format(member, time.ctime(time.time())))
            except:
                pass
            if not dat[0]:
                await conn.execute("UPDATE black_list SET name = '{0.name}' WHERE discord_id = '{0.id}'".format(member))
            await client.ban(member)
            return True
        except:
            pass
            await client.send_message(client.get_channel('480689437257498628'), "**{2}**\n``({0.name} | {0.mention}) != [{1.name} | {1.id}]``".format(member, member.server, time.ctime(time.time())))
            # await client.send_message(member.server.owner, "**{1}**\n``Не удалось кикнуть ({0.name} | {0.mention}) с твоего сервера '{0.server.name}' по причине нахождения в черном списке (DDOS-атаки) Tomori((``".format(member, time.ctime(time.time())))
        return True
    # if (datetime.utcnow() - member.created_at).days == 0:
    #     dat = await conn.fetchrow("SELECT name FROM black_list WHERE discord_id = '{}'".format(member.id))
    #     if dat:
    #         if not dat[0]:
    #             await conn.execute("UPDATE black_list SET name = '{0.name}' WHERE discord_id = '{0.id}'".format(member))
    #     else:
    #         await conn.execute("INSERT INTO black_list(name, discord_id) VALUES('{0.name}', '{0.id}')".format(member))
    #     try:
    #         await client.send_message(client.get_channel('480689437257498628'), "**{2}**\n``({0.name} | {0.mention}) кикнут потому что сегодня создан акк [{1.name} | {1.id}]``".format(member, member.server, time.ctime(time.time())))
    #         await client.send_message(member.server.owner, "**{1}**\n``С твоего сервера '{0.server.name}' кикнут ({0.name} | {0.mention}) по причине нахождения в черном списке (DDOS-атаки) Tomori.``".format(member, time.ctime(time.time())))
    #         await client.send_message(member, "**{1}**\n``Вас кикнули с сервера '{0.server.name}' по причине нахождения в черном списке (DDOS-атаки) Tomori. По вопросам разбана писать Ананасовая Печенюха [Cookie]#0001 (<@>282660110545846272)``".format(member, time.ctime(time.time())))
    #         await client.kick(member)
    #     except:
    #         await client.send_message(client.get_channel('480689437257498628'), "**{2}**\n``({0.name} | {0.mention}) не кикнут [{1.name} | {1.id}]``".format(member, member.server, time.ctime(time.time())))
    #     return True
    # if len(member.game.name.lower()) >= 30:# or (datetime.utcnow() - member.created_at).days == 0:
    #     dat = await conn.fetchrow("SELECT name FROM black_list WHERE discord_id = '{}'".format(member.id))
    #     if dat:
    #         if not dat[0]:
    #             await conn.execute("UPDATE black_list SET name = '{0.name}' WHERE discord_id = '{0.id}'".format(member))
    #     else:
    #         await conn.execute("INSERT INTO black_list(name, discord_id) VALUES('{0.name}', '{0.id}')".format(member))
    #     try:
    #         await client.send_message(client.get_channel('480689437257498628'), "**{2}**\n``({0.name} | {0.mention}) status> [{1.name} | {1.id}]``".format(member, member.server, time.ctime(time.time())))
    #         await client.send_message(member.server.owner, "**{1}**\n``С твоего сервера '{0.server.name}' кикнут ({0.name} | {0.mention}) по причине нахождения в черном списке (DDOS-атаки) Tomori.``".format(member, time.ctime(time.time())))
    #         #await client.send_message(member, "**{1}**\n``Вас кикнули с сервера '{0.server.name}' по причине нахождения в черном списке (DDOS-атаки) Tomori. По вопросам разбана писать Ананасовая Печенюха [Cookie]#0001 (<@>282660110545846272)``".format(member, time.ctime(time.time())))
    #         await client.kick(member)
    #     except:
    #         await client.send_message(client.get_channel('480689437257498628'), "**{2}**\n``({0.name} | {0.mention}) !status [{1.name} | {1.id}]``".format(member, member.server, time.ctime(time.time())))
    #     return True
    # for compare in ddos_name_list:
    #     if compare.lower() in member.name.lower():# or (datetime.utcnow() - member.created_at).days == 0:
    #         dat = await conn.fetchrow("SELECT name FROM black_list WHERE discord_id = '{}'".format(member.id))
    #         if dat:
    #             if not dat[0]:
    #                 await conn.execute("UPDATE black_list SET name = '{0.name}' WHERE discord_id = '{0.id}'".format(member))
    #         else:
    #             await conn.execute("INSERT INTO black_list(name, discord_id) VALUES('{0.name}', '{0.id}')".format(member))
    #         try:
    #             await client.send_message(client.get_channel('480689437257498628'), "**{2}**\n``({0.name} | {0.mention}) +> [{1.name} | {1.id}]``".format(member, member.server, time.ctime(time.time())))
    #             await client.send_message(member.server.owner, "**{1}**\n``С твоего сервера '{0.server.name}' кикнут ({0.name} | {0.mention}) по причине нахождения в черном списке (DDOS-атаки) Tomori.``".format(member, time.ctime(time.time())))
    #             #await client.send_message(member, "**{1}**\n``Вас кикнули с сервера '{0.server.name}' по причине нахождения в черном списке (DDOS-атаки) Tomori. По вопросам разбана писать Ананасовая Печенюха [Cookie]#0001 (<@>282660110545846272)``".format(member, time.ctime(time.time())))
    #             await client.ban(member)
    #         except:
    #             await client.send_message(client.get_channel('480689437257498628'), "**{2}**\n``({0.name} | {0.mention}) !- [{1.name} | {1.id}]``".format(member, member.server, time.ctime(time.time())))
    #         return True
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
    if server.splash_url:
        em.description = "Сервер (ID:{id}) invite:\n{invite}".format(id=server_id, invite=server.splash_url)
        await client.send_message(message.channel, embed=em)
        return
    try:
        invite = await client.create_invite(server, max_age=0, max_uses=0)
        em.description = "Сервер (ID:{id}) invite created:\n{invite}".format(id=server_id, invite=invite.url)
        await client.send_message(message.channel, embed=em)
        return
    except:
        pass
    for channel in server.channels:
        try:
            invite = await client.create_invite(channel, max_age=0, max_uses=0)
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
    dat = await conn.fetchrow("SELECT * FROM tickets WHERE request_id = '{request_id}' OR response_id = '{response_id}'".format(request_id=chan_id, response_id=chan_id))
    if not dat:
        if channel.is_private and message.content:
            content = message.content
            dialogflow = apiai.ApiAI('93004d9d5f464d4daa2204896b2f9a35').text_request()
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
                    await client.send_message(message.author, '{mention}, я Вас не совсем поняла!'.format(mention=message.author.mention))
            except:
                pass
        return

    request_channel = u_get_channel(client, dat["request_id"])
    response_channel_id = dat["response_id"]
    if not message.author.bot and request_channel and not message.content == "" and not message.content == "!stop":
        em = discord.Embed(colour=0xC5934B)
        em.description = message.content
        if not channel.is_private:
            if channel.id == response_channel_id:
                index = 0
                name = None
                for s in support_list:
                    index += 1
                    if s == message.author.id:
                        name = "Агент поддержки#000{tag} ✔".format(tag=index)
                        icon_url = client.user.avatar_url
                        break
                if dat["name"]:
                    name = "{name}#{tag}".format(name=dat["name"], tag=message.author.discriminator)
                    icon_url = message.server.icon_url
                if not name:
                    name = "{name}#{tag}".format(name=message.author.name, tag=message.author.discriminator)
                    icon_url = message.author.avatar_url
                em.set_author(name=name, icon_url=icon_url)
                await client.send_message(request_channel, embed=em)
            elif channel.id == request_channel.id:
                em.set_author(name=message.author.name + "#" + message.author.discriminator, icon_url=message.author.avatar_url)
                em.set_footer(text="ID: {id} • Mention: {mention}".format(
                    id=message.author.id,
                    mention=message.author.mention
                ))
                await client.send_message(u_get_channel(client, response_channel_id), embed=em)
        else:
            if channel.user.id == request_channel.id:
                em.set_author(name=message.author.name + "#" + message.author.discriminator, icon_url=message.author.avatar_url)
                em.set_footer(text="ID: {id} • Mention: {mention}".format(
                    id=message.author.id,
                    mention=message.author.mention
                ))
                await client.send_message(u_get_channel(client, response_channel_id), embed=em)
            elif channel.user.id == response_channel_id:
                index = 0
                name = None
                for s in support_list:
                    index += 1
                    if s == message.author.id:
                        name = "Агент поддержки#000{tag} ✔".format(tag=index)
                        icon_url = client.user.avatar_url
                        break
                if dat["name"]:
                    name = "{name}#{tag}".format(name=dat["name"], tag=message.author.discriminator)
                    icon_url = message.author.avatar_url
                if not name:
                    name = "{name}#{tag}".format(name=message.author.name, tag=message.author.discriminator)
                    icon_url = message.author.avatar_url
                em.set_author(name=name, icon_url=icon_url)
                await client.send_message(request_channel, embed=em)
