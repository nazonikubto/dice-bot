import os
import re
import random
import discord
from discord.ext import commands
from discord import Embed
from flask import Flask
import threading

# Flaskアプリ（Render用）
app = Flask(__name__)

@app.route("/")
def index():
    return "Bot is running!"

# Discord Bot 設定
TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    raise ValueError("DISCORD_TOKEN が環境変数にありません")

intents = discord.Intents.default()
intents.message_content = True

# 「うお」だけで反応（!は不要）
bot = commands.Bot(command_prefix="", intents=intents)

@bot.event
async def on_ready():
    print(f"{bot.user} が起動しました！")

# ダイス式のパーサー
def parse_dice_expression(expression: str):
    expression = expression.replace("＋", "+").replace("−", "-")  # 全角対応
    tokens = re.findall(r'(\d*d\d+|\d+|[+\-])', expression)  # 1d100, 5, +, -
    total = 0
    detail = []
    last_op = '+'

    for token in tokens:
        if token in ('+', '-'):
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
    return total, detail

# 「うお」コマンド（ダイス）
@bot.command(name="うお")
async def dice(ctx, *, expression: str):
    try:
        total, detail = parse_dice_expression(expression)
        embed = Embed(title="🎲 ダイス結果", description="\n".join(detail), color=0x00ffcc)
        embed.add_field(name="合計", value=str(total), inline=False)
        await ctx.send(embed=embed)
    except Exception:
        await ctx.send("⚠️ 正しい形式で入力してください。例: `うお 1d100+1d10+5`")

# 「cd」判定
@bot.command(name="cd")
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
        if not (1 <= n <= 100):
            await ctx.send("1〜100の範囲で指定してください")
            return
        outcome = f"🎯 成功！（{result} ≤ {n}）" if result <= n else f"💥 失敗…（{result} > {n}）"

    embed = Embed(title="🎲 1d100判定", description=f"出目: **{result}**", color=0x66ccff)
    embed.add_field(name="結果", value=outcome, inline=False)
    await ctx.send(embed=embed)

# 「choice」コマンド
@bot.command(name="choice")
async def choice(ctx, *options: str):
    if len(options) < 2:
        await ctx.send("⚠️ 選択肢は2つ以上必要です。例: `choice 赤 青`")
        return
    selected = random.choice(options)
    embed = Embed(title="🎯 選択", description=f"選ばれたのは **{selected}**", color=0xff99cc)
    await ctx.send(embed=embed)

# Botを別スレッドで起動（Render用）
def run_bot():
    bot.run(TOKEN)

threading.Thread(target=run_bot).start()



