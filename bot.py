import os
import re
import random
import discord
from discord.ext import commands

TOKEN = os.environ.get('DISCORD_TOKEN')
if not TOKEN:
    raise ValueError("DISCORD_TOKEN が環境変数にありません")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'{bot.user.name} が起動しました！')

# 複雑なダイス式に対応
def parse_dice_expression(expression):
    pattern = r'(\d*)d(\d+)|([-+]?\d+)'
    tokens = re.findall(pattern, expression.replace("＋", "+").replace("－", "-"))
    total = 0
    details = []

    for dice_count, dice_sides, modifier in tokens:
        if dice_sides:  # ダイスロール
            count = int(dice_count) if dice_count else 1
            sides = int(dice_sides)
            rolls = [random.randint(1, sides) for _ in range(count)]
            subtotal = sum(rolls)
            total += subtotal
            details.append(f"{count}d{sides}: {rolls} → {subtotal}")
        elif modifier:  # 定数加算
            value = int(modifier)
            total += value
            details.append(f"{value:+d}")

    return total, details

# !1d100 などに対応（正規表現でマッチ）
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    content = message.content.replace("！", "!")  # 全角から半角に変換

    # 1d100 のようなコマンドに対応
    if content.startswith('!') and re.match(r'^!\s*[\dd+\-d\s]+$', content):
        expression = content[1:].strip()
        try:
            total, details = parse_dice_expression(expression)
            embed = discord.Embed(title="🎲 ダイスロール結果", color=0x00ffcc)
            embed.add_field(name="式", value=expression, inline=False)
            embed.add_field(name="内訳", value='\n'.join(details), inline=False)
            embed.add_field(name="合計", value=f"**{total}**", inline=False)
            await message.channel.send(embed=embed)
        except Exception:
            await message.channel.send("❌ ダイス式の解析に失敗しました。")
        return

    await bot.process_commands(message)

# うおコマンド（旧 !cd）
@bot.command(name="うお")
async def uo(ctx, n: int = None):
    result = random.randint(1, 100)
    if n is None:
        if result <= 5:
            outcome = "🎯 **クリティカル（決定的成功）！**"
        elif result >= 96:
            outcome = "💥 **ファンブル（致命的失敗）！**"
        else:
            outcome = ""
    else:
        if not (1 <= n <= 100):
            await ctx.send("1〜100の整数で指定してください。例: `!うお 50`")
            return
        if result <= n:
            outcome = f"✅ 成功！({result} ≤ {n})"
        else:
            outcome = f"❌ 失敗…({result} > {n})"

    embed = discord.Embed(title="🎲 1d100 判定", color=0x6699ff)
    embed.add_field(name="出目", value=f"**{result}**", inline=True)
    if outcome:
        embed.add_field(name="結果", value=outcome, inline=False)
    await ctx.send(embed=embed)

# 選択コマンド（全角/半角対応）
@bot.command()
async def choice(ctx, *options: str):
    options = [opt.strip() for opt in options if opt.strip()]
    if len(options) < 2:
        await ctx.send("選択肢は2つ以上指定してください。例: `!choice 赤 青`")
        return
    selected = random.choice(options)
    embed = discord.Embed(title="🎯 選択結果", description=f"選ばれたのは：**{selected}**", color=0xffcc00)
    await ctx.send(embed=embed)

# gunicorn用
def start_bot():
    bot.run(TOKEN)

