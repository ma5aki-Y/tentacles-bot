import discord
from discord.ext import commands

from modules.stage import StageInfo

TOKEN = os.environ['BOT_TOKEN']

bot = commands.Bot(command_prefix='/')

@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))

@bot.command(name='st')
async def show_stage(ctx, *args):
    stage_info = StageInfo()
    regular = stage_info.get_regular(ctx)
    ranked = stage_info.get_ranked(ctx)
    league = stage_info.get_league(ctx)
    salmon = stage_info.get_salmon(ctx)

    if len(args) > 2 :
        await ctx.channel.send("引数が多いようです...")
    elif len(args) == 0:
        embeds = [regular,ranked,league,salmon]
        for embed in embeds:
            await ctx.channel.send(embed=embed)
        return

    if args[0] == 'regular':
        await ctx.channel.send(embed=regular)
        return
    elif args[0] == 'ranked':
        await ctx.channel.send(embed=ranked)
        return
    elif args[0] == 'league':
        await ctx.channel.send(embed=league)
        return
    elif args[0] == 'salmon':
        await ctx.channel.send(embed=salmon)
        return
    else:
        await ctx.channel.send("引数がおかしいようです...")
        return

bot.run(TOKEN)