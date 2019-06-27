import json
import requests
import time
import datetime
import discord
import asyncio
import aiohttp
from aiohttp import ClientSession
from collections import defaultdict

loop = asyncio.get_event_loop()

class Webhook:
    def __init__(self, web_url, **kwargs):

        """
        Initialise a Webhook Embed Object
        """

        self.web_url = web_url
        self.text = kwargs.get('text')
        self.color = kwargs.get('color')
        self.username = kwargs.get('username')
        self.avatar_url = kwargs.get('avatar_url')
        self.title = kwargs.get('title')
        self.title_url = kwargs.get('title_url')
        try:
            self.author = kwargs.get('author').get("name")
        except:
            self.author = None
        try:
            self.author_icon = kwargs.get('author').get("icon_url")
        except:
            self.author_icon = discord.Embed.Empty
        try:
            self.author_url = kwargs.get('author').get("url")
        except:
            self.author_url = discord.Embed.Empty
        self.description = kwargs.get('description')
        self.fields = kwargs.get('fields', [])
        self.image = kwargs.get('image')
        self.thumbnail = kwargs.get('thumbnail')
        try:
            self.footer = kwargs.get('footer').get("text")
        except:
            self.footer = discord.Embed.Empty
        try:
            self.footer_icon = kwargs.get('footer').get("icon_url")
        except:
            self.footer_icon = discord.Embed.Empty
        self.timestamp = str(kwargs.get('timestamp')) if kwargs.get('timestamp') else None
        if kwargs.get('ts'):
            self.timestamp = str(kwargs.get('ts'))


    def add_field(self,**kwargs):
        '''Adds a field to `self.fields`'''
        name = kwargs.get('name')
        value = kwargs.get('value')
        inline = kwargs.get('inline', True)

        field = {

        'name' : name,
        'value' : value,
        'inline' : inline

        }

        self.fields.append(field)

    def set_description(self,description):
        self.description = description

    def set_author(self, **kwargs):
        self.author = kwargs.get('name')
        self.author_icon = kwargs.get('icon')
        self.author_url = kwargs.get('url')

    def set_title(self, **kwargs):
        self.title = kwargs.get('title')
        self.title_url = kwargs.get('url')

    def set_thumbnail(self, url):
        self.thumbnail = url

    def set_image(self, url):
        self.image = url

    def set_footer(self,**kwargs):
        self.footer = kwargs.get('text')
        self.footer_icon = kwargs.get('icon')
        timestamp = kwargs.get('timestamp')
        if timestamp == True:
            self.timestamp = str(datetime.datetime.utcfromtimestamp(time.time()))
        else:
            self.timestamp = str(datetime.datetime.utcfromtimestamp(timestamp))


    def del_field(self, index):
        self.fields.pop(index)

    @property
    def json(self,*arg):
        '''
        Formats the data into a payload
        '''

        data = {}

        data["embeds"] = []
        embed = defaultdict(dict)
        if self.text: data["content"] = self.text
        if self.author: embed["author"]["name"] = self.author
        if self.author_icon: embed["author"]["icon_url"] = self.author_icon
        if self.author_url: embed["author"]["url"] = self.author_url
        if self.color: embed["color"] = self.color
        if self.description: embed["description"] = self.description
        if self.title: embed["title"] = self.title
        if self.title_url: embed["url"] = self.title_url
        if self.image: embed["image"]['url'] = self.image
        if self.thumbnail: embed["thumbnail"]['url'] = self.thumbnail
        if self.footer: embed["footer"]['text'] = self.footer
        if self.footer_icon: embed['footer']['icon_url'] = self.footer_icon
        if self.timestamp: embed["timestamp"] = self.timestamp
        if self.username: data["username"] = self.username
        if self.avatar_url: data["avatar_url"] = self.avatar_url

        if self.fields:
            embed["fields"] = []
            for field in self.fields:
                f = {}
                f["name"] = field['name']
                f["value"] = field['value']
                f["inline"] = field['inline']
                embed["fields"].append(f)

        data["embeds"].append(dict(embed))

        empty = all(not d for d in data["embeds"])

        if empty and 'content' not in data:
            print('You cant post an empty payload.')
        if empty: data['embeds'] = []

        return json.dumps(data, indent=4)




    async def post(self):
        headers = {
            'Content-Type': 'application/json'
        }

        async with ClientSession(loop=loop) as session:
            async with session.post(self.web_url, data=self.json, headers=headers) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return None
