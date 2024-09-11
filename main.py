import discord
from discord.ext import commands
import subprocess
import json

def message_load():
    with open("message.json", encoding="utf-8_sig") as file:
        message_list = json.load(file)
    return message_list

message = message_load()
word = message["word"]
success = message["success"]
error = message["error"]
rec_len = len(word["record"])

admin = 378480271965683713 # kaka_256 user_id

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')
    await bot.tree.sync()

# send server status
@bot.hybrid_command()
async def send_message(ctx, channel_id):
    channel_obj = bot.get_channel(int(channel_id))
    if not channel_obj:
        await ctx.send("error")
    else:
        await ctx.send(success["send"])
        await channel_obj.send("test")
        await ctx.send(success["send_end"])

# nickname change command
@bot.hybrid_command()
async def rec(ctx):
    nickname = f"{ctx.author.name}{word['record']}"
    if not ctx.author.nick:
        pass

    elif ctx.author.nick[:-rec_len] == ctx.author.name:
        nickname = None

    elif ctx.author.nick[-rec_len:] == word['record']:
        nickname = ctx.author.nick[:-rec_len]

    try:
        await ctx.author.edit(nick = nickname)
        await ctx.reply(success["chenged"])
    except:
        await ctx.reply(error["permission"])

# bot exit command. only use admin
@bot.hybrid_command()
async def exit(ctx):
    if ctx.author.id == admin:
        print("exit")
        await ctx.reply("exit")
        await bot.close()
        await ctx.reply(error["feilure"])
    else:
        await ctx.reply(error["permisson"])

# reboot command. os reboot. only use admin
@bot.hybrid_command()
async def reboot(ctx):
    if ctx.author.id == admin:
        print("reboot")
        await ctx.reply("reboot")
        subprocess.call("reboot")
        await bot.close()
        await ctx.reply(error["feilure"])
    else:
        await ctx.reply(error["permisson"])

with open("token.json") as file:
    token = json.load(file)
bot.run(token["token"])