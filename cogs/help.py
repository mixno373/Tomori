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


async def h_check_help(client, message, _locale, em, prefix):
    name = message.content.split(" ", maxsplit=1)
    name = name[1]

    em.title = _locale["help_name"].format(name=name)
    em.set_footer(text="{name}#{discriminator}".format(
        name=message.author.name,
        discriminator=message.author.discriminator
    ))

    #await client.send_message(message.channel, embed=em)
    if "help_"+name+"_desc" in _locale.keys():
        usage = ""
        example = ""
        if "help_"+name+"_usage" in _locale.keys():
            usage = "\n\n"+_locale["help_"+name+"_usage"].format(prefix=prefix)
        if "help_"+name+"_example" in _locale.keys():
            example = "\n"+_locale["help_"+name+"_example"].format(prefix=prefix)
        em.description = "{desc}{usage}{example}".format(
            desc=_locale["help_"+name+"_desc"],
            usage=usage,
            example=example
            )
    else:
        em.description = _locale["help_command_not_found"]
    await client.send_message(message.channel, embed=em)
    return
