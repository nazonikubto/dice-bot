import os
import re
import random
import discord
from discord.ext import commands
from discord import app_commands, Embed

# トークン取得
TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    raise ValueError("DISCORD_TOKEN が環境変数にありません")

# Bot初期化（prefix付きコマンドは"!"限定）
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"{bot.user} が起動しました！")

# 1d100 → [50]
# 2d6+1d4+3 → [1,5] + [2] + 3 = 11
@bot.command(aliases=["roll"])
async def dice(ctx, *, expression: str):
    expression = expression.replace("＋", "+").replace("−", "-")  # 全角対応
    try:
        tokens = re.findall(r'(\d*d\d+|\d+|[+\-])', expression)
        total = 0
        detail = []
        last_op = '+'

        for token in tokens:
            if token in '+-':
                last_op = token
            elif 'd' in token:
                num, sides = token.split('d')
                num = int(num) if num else 1
                sides = int(sides)
                rolls = [random.randint(1, sides) for _ in range(num)]
                subtotal = sum(rolls)
                detail.append(f"{token} → {rolls} = {subtotal}")
                total = total + subtotal if last_op == '+' else total - subtotal
            else:
                value = int(token)
                detail.append(f"{last_op}{value}")
                total = total + value if last_op == '+' else total - value

        embed = Embed(title="🎲 ダイス結果", description="\n".join(detail), color=0x00ffcc)
        embed.add_field(name="合計", value=str(total), inline=False)
        await ctx.send(embed=embed)
    except Exception as e:
        await ctx.send("⚠️ コマンドが正しくありません。例: `!1d100+1d10+5`")

# !cd で判定（クリティカル/ファンブル）
@bot.command()
async def cd(ctx, n: int = None):
    result = random.randint(1, 100)

    if n is None:
        if result <= 5:
            outcome = "🎯 **クリティカル（決定的成功）！**"
        elif result >= 96:
            outcome = "💥 **ファンブル（致命的失敗）！**"
        else:
            outcome = "成功 or 失敗（閾値未指定）"
    else:
        if not 1 <= n <= 100:
            await ctx.send("1〜100の範囲で指定してください")
            return
        outcome = f"🎯 成功！（{result} ≤ {n}）" if result <= n else f"💥 失敗…（{result} > {n}）"

    embed = Embed(title="🎲 1d100判定", description=f"出目: **{result}**", color=0x66ccff)
    embed.add_field(name="結果", value=outcome, inline=False)
    await ctx.send(embed=embed)

# !choice 赤 青 緑 / 全角も可
@bot.command()
async def choice(ctx, *options: str):
    if len(options) < 2:
        await ctx.send("⚠️ 選択肢は2つ以上必要です。例: `!choice 赤 青`")
        return
    selected = random.choice(options)
    embed = Embed(title="🎯 選択", description=f"選ばれたのは **{selected}**", color=0xff99cc)
    await ctx.send(embed=embed)

# "うお" だけで反応させる（通常メッセージ監視）
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    # うお → ダイス判定
    if message.content.strip() == "うお":
        result = random.randint(1, 100)
        if result <= 5:
            outcome = "🎯 **クリティカル（決定的成功）！**"
        elif result >= 96:
            outcome = "💥 **ファンブル（致命的失敗）！**"
        else:
            outcome = "成功 or 失敗（閾値未指定）"

        embed = Embed(title="🎲 1d100判定", description=f"出目: **{result}**", color=0x66ccff)
        embed.add_field(name="結果", value=outcome, inline=False)
        await message.channel.send(embed=embed)

    # 他のコマンドも通す
    await bot.process_commands(message)

# Bot起動（Render上では使わない）
if __name__ == "__main__":
    bot.run(TOKEN)
