import os
import random
import re
import discord
from discord.ext import commands
from keep_alive import keep_alive

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ダイス処理：1d100+1d10など複雑な式対応
dice_pattern = re.compile(r'(\d*)d(\d+)', re.IGNORECASE)

def parse_dice_expression(expression):
    tokens = re.split(r'(\+|\-)', expression.replace(" ", ""))
    total = 0
    details = []
    current_sign = 1

    for token in tokens:
        token = token.strip()
        if token == '+':
            current_sign = 1
        elif token == '-':
            current_sign = -1
        elif dice_pattern.fullmatch(token):  # 1d100 など
            match = dice_pattern.fullmatch(token)
            count = int(match.group(1)) if match.group(1) else 1
            sides = int(match.group(2))
            rolls = [random.randint(1, sides) for _ in range(count)]
            subtotal = sum(rolls)
            total += current_sign * subtotal
            details.append(f"{'-' if current_sign == -1 else ''}{count}d{sides} ➝ {rolls} = {subtotal}")
        elif token.isdigit():  # 定数加算
            val = int(token)
            total += current_sign * val
            details.append(f"{'-' if current_sign == -1 else ''}{val}")
        else:
            return None, f"❌ 無効なダイス式: {token}"

    return total, "\n".join(details)

# コマンド: !1d100 や !2d6+5 対応
@bot.command(name='roll')
async def roll(ctx, *, expression: str):
    total, details = parse_dice_expression(expression)
    if total is None:
        await ctx.send(details)
        return

    embed = discord.Embed(title="🎲 ダイス結果", color=discord.Color.blue())
    embed.add_field(name="計算式", value=expression, inline=False)
    embed.add_field(name="詳細", value=details, inline=False)
    embed.add_field(name="合計", value=f"**{total}**", inline=False)
    await ctx.send(embed=embed)

# !うお または うお で成功判定（cd コマンドの改名）
@bot.command(name="うお")
async def success_check(ctx, threshold: int):
    roll = random.randint(1, 100)
    result = "✅ 成功！" if roll <= threshold else "❌ 失敗！"
    embed = discord.Embed(title="🎯 成功判定", color=discord.Color.green() if roll <= threshold else discord.Color.red())
    embed.add_field(name="目標値", value=str(threshold), inline=True)
    embed.add_field(name="出目", value=str(roll), inline=True)
    embed.add_field(name="判定", value=result, inline=False)
    await ctx.send(embed=embed)

# !choice コマンド：2個以上に対応 & 全角/半角スペース対応
@bot.command(name='choice')
async def choose(ctx, *, args: str):
    options = re.split(r'[ 　]+', args.strip())  # 半角/全角スペース両対応
    if len(options) < 2:
        await ctx.send("⚠️ 2つ以上の選択肢を入力してください！")
        return
    result = random.choice(options)
    embed = discord.Embed(title="🎲 選択結果", description=result, color=discord.Color.purple())
    await ctx.send(embed=embed)

# !省略のため on_message を使う
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    # !を省略したうおにも対応
    if message.content.startswith("うお"):
        parts = message.content[2:].strip()
        if parts.isdigit():
            ctx = await bot.get_context(message)
            await success_check(ctx, int(parts))
            return

    # !1d100 のような短縮コマンド
    if message.content.startswith("!"):
        expr = message.content[1:]
        if dice_pattern.search(expr):
            ctx = await bot.get_context(message)
            await roll(ctx, expression=expr)
            return

    await bot.process_commands(message)

# 起動
keep_alive()
TOKEN = os.environ.get("DISCORD_TOKEN")
bot.run(TOKEN)
