import discord
import asyncio
import re
import logging
import json
from config.constants import *


monitoring_channels = {
	"497104731223621643": {
			"latest": "Недавно лайкнутые сервера",
			"top": "Лучшие сервера",
            "locale": "russian"
		},
	"497103000028839956": {
			"latest": "Recently liked servers",
			"top": "The best servers",
            "locale": "english"
		}
}

daily_monitoring_channels = {
	"524158395268333568": {
            "locale": "russian"
		},
	"524158621232267264": {
            "locale": "english"
		}
}



servers_with_removing_urls = {
	"564829247810568193": 1
}




report_channel_id = "497413275789688833"

monitoring_server_id = "497093762464350208"


servers_without_more_info_in_help = [
"502913055559254036"
]

servers_without_follow_us = [
"502913055559254036",
"433350258941100032",
"485400595235340303",
"455121989825331200",
"458947364137467906"
]

konoha_servers = [
"502913055559254036"
]

not_monitoring_servers = [
"491961477926748162",
"502412345046466561",
"458947364137467906"
]

travelling_servers = {
    "530393892428840970": "320617533231202304"  # New Year Tide
}

travelling_message_servers = {}

# tomori_event_channel = "480857367165272064"
