import discord.ext.commands as commands
from config.settings import *
from cogs.const import *

bot = commands.Bot(commands.when_mentioned_or(prefix_list))
bot.load_extension('cogs.music')

@bot.command()
@commands.has_permissions(manage_guild=True)
async def reload(ctx):
    ctx.bot.unload_extension('cogs.music')
    ctx.bot.load_extension('cogs.music')
    await ctx.message.add_reaction('\N{WHITE HEAVY CHECK MARK}')

bot.run(settings["token"])
