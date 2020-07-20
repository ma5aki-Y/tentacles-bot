import urllib.request
from datetime import datetime as dt
from datetime import timedelta, timezone
import json

import discord

class StageInfo:
    base_url = 'https://spla2.yuu26.com/'

    def __init__(self):
        self.state_err = '取得に失敗したようです...'

    def get_regular(self, ctx):
        now = self.http_get(self.base_url + 'regular/now')
        nex = self.http_get(self.base_url + 'regular/next')
        embed = discord.Embed(title="レギュラーマッチ",color=0xc9f420)
        embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/490190589292445698/709525374391943185/regular.png")

        embed.add_field(name="現在のステージ({0} まで)".format(dt.strptime(now['result'][0]['end'], '%Y-%m-%dT%H:%M:%S').strftime('%m/%d %H:%M')),
         value="{0}\n{1}".format(now['result'][0]['maps'][0], now['result'][0]['maps'][1]), inline=False)
        embed.add_field(name="次のステージ({0} から)".format(dt.strptime(nex['result'][0]['start'], '%Y-%m-%dT%H:%M:%S').strftime('%m/%d %H:%M')),
         value="{0}\n{1}".format(nex['result'][0]['maps'][0], nex['result'][0]['maps'][1]), inline=False)

        return embed

    def get_ranked(self, ctx):
        now = self.http_get(self.base_url + 'gachi/now')
        nex = self.http_get(self.base_url + 'gachi/next')
        embed = discord.Embed(title="ガチマッチ",color=0xf43e0a)
        embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/490190589292445698/709525376019464202/gachi.png")
        self.set_now_stage_to_embed(ctx, embed, now)
        self.set_next_stage_to_embed(ctx, embed, nex)

        return embed

    def get_league(self, ctx):
        now = self.http_get(self.base_url + 'league/now')
        nex = self.http_get(self.base_url + 'league/next')
        embed = discord.Embed(title="リーグマッチ",color=0xee2473)
        embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/490190589292445698/709525398047948880/league.png")

        self.set_now_stage_to_embed(ctx, embed, now)
        self.set_next_stage_to_embed(ctx, embed, nex)

        return embed

    def get_salmon(self, ctx):
        JST = timezone(timedelta(hours=+9), 'JST')
        now = dt.now(JST)

        res = self.http_get(self.base_url + 'coop/schedule')

        start = dt.strptime(res['result'][0]['start'], '%Y-%m-%dT%H:%M:%S')
        end = dt.strptime(res['result'][0]['end'], '%Y-%m-%dT%H:%M:%S')
        weapons = res['result'][0]['weapons']

        embed = discord.Embed(title="サーモンラン",color=0xecf150)
        embed.set_thumbnail(url=res['result'][0]['stage']['image'])

        if now.timestamp() >= start.timestamp():
            embed.add_field(name="バイト募集中！", value="__{0}__ まで".format(end.strftime('%m/%d %H:%M'), inline=True))
        else:
            embed.add_field(name="現在バイトは募集しておりません。", value="次のバイトは__{0}__ から".format(start.strftime('%m/%d %H:%M')), inline=True)

        embed.add_field(name="ステージは", value=res['result'][0]['stage']['name'], inline=True)
        embed.add_field(name="支給ブキは", value="・{0}\n・{1}\n・{2}\n・{3}".format(weapons[0]['name'], weapons[1]['name'], weapons[2]['name'], weapons[3]['name']), inline=False)

        return embed

    def set_now_stage_to_embed(self, ctx, embed, now):
        embed.add_field(name="現在のステージ({0} まで)".format(dt.strptime(now['result'][0]['end'], '%Y-%m-%dT%H:%M:%S').strftime('%m/%d %H:%M')),
         value="__{0}__\n→{1}\n→{2}".format(now['result'][0]['rule'],now['result'][0]['maps'][0], now['result'][0]['maps'][1]), inline=False)
        
    def set_next_stage_to_embed(self, ctx, embed, nex):
        embed.add_field(name="次のステージ({0} から)".format(dt.strptime(nex['result'][0]['start'], '%Y-%m-%dT%H:%M:%S').strftime('%m/%d %H:%M')),
         value="__{0}__\n→{1}\n→{2}".format(nex['result'][0]['rule'],nex['result'][0]['maps'][0], nex['result'][0]['maps'][1]), inline=False)

    def http_get(self, url):
        req = urllib.request.Request(url)
        try:
            with urllib.request.urlopen(req) as res:
                body = json.load(res)
        except urllib.error.HTTPError:
            return self.state_err
        except urllib.error.URLError:
            return self.state_err

        return body