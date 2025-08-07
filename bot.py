import os
import random
import discord
from discord.ext import commands
from keep_alive import keep_alive  # Replitでの自動再起動用Webサーバー

# ReplitのSecretsからトークンを取得
TOKEN = os.environ.get('DISCORD_TOKEN')
if not TOKEN:
    raise ValueError("SecretsにDISCORD_TOKENが設定されていません。")

# Discordの意図（intents）設定
intents = discord.Intents.default()
intents.message_content = True

# Bot初期化
bot = commands.Bot(command_prefix='!', intents=intents)

# 起動確認イベント
@bot.event
async def on_ready():
    print(f'{bot.user.name} が起動しました！')

# ダイスロールコマンド
@bot.command()
async def roll(ctx, *, dice: str):
    try:
        rolls = dice.lower().split()
        results = []
        for roll in rolls:
            if 'd' not in roll:
                await ctx.send("ダイス形式が正しくありません。例: `!roll 2d6`")
                return
            num, sides = map(int, roll.split('d'))
            result = [random.randint(1, sides) for _ in range(num)]
            results.append(f"{roll}: {result} = {sum(result)}")
        await ctx.send('\n'.join(results))
    except Exception:
        await ctx.send("エラー: 正しい形式で入力してください。例: `!roll 2d6`")

# クリティカル・ファンブル判定
@bot.command()
async def cd(ctx, n: int = None):
    result = random.randint(1, 100)
    if n is None:
        if result <= 5:
            outcome = "🎯 **クリティカル（決定的成功）！**"
        elif result >= 96:
            outcome = "💥 **ファンブル（致命的失敗）！**"
        else:
            outcome = "通常成功"
    else:
        if not (1 <= n <= 100):
            await ctx.send("1〜100の整数で指定してください。例: `!cd 50`")
            return
        if result <= n:
            outcome = f"成功！({result} ≤ {n})"
        else:
            outcome = f"失敗…({result} > {n})"
    await ctx.send(f"1d100 → {result}\n結果: {outcome}")

# 選択肢からランダムに選ぶ
@bot.command()
async def choice(ctx, *options: str):
    if len(options) < 2:
        await ctx.send("選択肢は2つ以上指定してください。例: `!choice 赤 青`")
        return
    selected = random.choice(options)
    await ctx.send(f"選ばれたのは: {selected}")

# ReplitのWebサーバーを起動（ping対策）
keep_alive()

# Botを起動
bot.run(TOKEN)

