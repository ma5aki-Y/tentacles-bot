import random

import discord
from discord.ext import commands

import os

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

    if len(args) >= 2:
        await ctx.channel.send("引数が多いようです...")
        return
    elif len(args) == 0:
        embeds = [regular, ranked, league, salmon]
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


class ShuffleButtonView(discord.ui.View):
    def __init__(self):
        super().__init__()

        self.add_item(ReadyButton())
        self.add_item(RetryButton())


class ReadyButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="これでいく！", style=discord.ButtonStyle.green)

    async def callback(self, interaction: discord.Interaction):
        alpha_ch = ""
        bravo_ch = ""
        for vc in interaction.guild.voice_channels:
            if vc.name == "alpha":
                alpha_ch = vc
            elif vc.name == "bravo":
                bravo_ch = vc

        alpha = interaction.message.content.split("\n")[0].split()[1:]
        bravo = interaction.message.content.split("\n")[1].split()[1:]
        for member_name in alpha:
            await interaction.guild.get_member_named(member_name).move_to(alpha_ch)

        for member_name in bravo:
            await interaction.guild.get_member_named(member_name).move_to(bravo_ch)

        await interaction.message.channel.send("チーム分け完了！ \n", view=ComeBuckButtonView())
        await interaction.message.delete()


class RetryButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="もう一回！", style=discord.ButtonStyle.red)

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.voice is None:
            await interaction.message.channel.send("ボイスチャンネルに入ってね!")
            return

        name = list(split_list([member.name for member in interaction.user.voice.channel.members]))
        await interaction.message.channel.send(gen_team_split_message(name), view=ShuffleButtonView())
        await interaction.message.delete()


class ComeBuckButtonView(discord.ui.View):
    def __init__(self):
        super().__init__()

        self.add_item(ComeBuckButton())


class ComeBuckButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="ロビーに戻す", style=discord.ButtonStyle.green)

    async def callback(self, interaction: discord.Interaction):
        alpha_ch = ""
        bravo_ch = ""
        lobby_ch = ""
        for vc in interaction.guild.voice_channels:
            if vc.name == "alpha":
                alpha_ch = vc
            elif vc.name == "bravo":
                bravo_ch = vc
            elif vc.name == "ロビー":
                lobby_ch = vc

        for member in alpha_ch.members:
            await member.move_to(lobby_ch)

        for member in bravo_ch.members:
            await member.move_to(lobby_ch)

        await interaction.message.channel.send("戻したよ！", view=ReShuffleButtonView())
        await interaction.message.delete()


class ReShuffleButtonView(discord.ui.View):
    def __init__(self):
        super().__init__()

        self.add_item(ReShuffleButton())


class ReShuffleButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="またチーム分けする", style=discord.ButtonStyle.green)

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.voice is None:
            await interaction.message.channel.send("ボイスチャンネルに入ってね!")
            return

        name = list(split_list([member.name for member in interaction.user.voice.channel.members]))
        await interaction.message.channel.send(gen_team_split_message(name), view=ShuffleButtonView())
        await interaction.message.delete()


def split_list(members):
    random.shuffle(members)
    yield members[0:len(members) // 2]
    yield members[len(members) // 2:]


def gen_team_split_message(members):
    return ":a: " + " ".join(members[0]) + "\n" + ":regional_indicator_b: " + " ".join(members[1])


@bot.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return
    if message.content.startswith("/team"):
        if message.author.voice is None:
            await message.channel.send("ボイスチャンネルに入ってね!")
            return
        if len(message.author.voice.channel.members) < 2:
            await message.channel.send("二人以上で試してね！")
            return

        if "ロビー" not in [channel.name for channel in message.author.voice.channel.category.voice_channels]:
            await message.author.voice.channel.category.create_voice_channel("ロビー")

        if "alpha" not in [channel.name for channel in message.author.voice.channel.category.voice_channels]:
            await message.author.voice.channel.category.create_voice_channel("alpha")

        if "bravo" not in [channel.name for channel in message.author.voice.channel.category.voice_channels]:
            await message.author.voice.channel.category.create_voice_channel("bravo")

        lobby_ch = ""
        for vc in message.author.voice.channel.category.voice_channels:
            if vc.name == "ロビー":
                lobby_ch = vc

        for member in message.author.voice.channel.members:
            await member.move_to(lobby_ch)

        members = list(split_list([member.name for member in message.author.voice.channel.members]))
        await message.channel.send(gen_team_split_message(members), view=ShuffleButtonView())


bot.run(TOKEN)
