import discord
from discord.ext import commands
import subprocess
import json

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

class bot_data():
    def __init__(self):
        self.message_load()
        self.data_load()

    def message_load(self):
        with open("resource/message.json", encoding="utf-8_sig") as file:
            message = json.load(file)
            
        self.word = message["word"]
        self.success = message["success"]
        self.error = message["error"]
        self.rec_len = len(self.word["record"])
    def data_load(self):
        with open("resource/data.json", encoding="utf-8_sig") as file:
            data = json.load(file)
        self.admin = data["admin"]
        self.status_data = data["status"]

data_class = bot_data()

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')
    await bot.tree.sync()

@bot.command()
async def message_reload(ctx):
    data_class.message_load()
    await ctx.send("reload")

@bot.command()
async def data_reload(ctx):
    data_class.data_load()
    await ctx.send("reload")

# send server status
@bot.hybrid_command()
async def send_message(ctx, channel_id, game):
    channel_obj = bot.get_channel(int(channel_id))
    game = game.lower()
    text = ""
    if not channel_obj or not game in data_class.word["status"]:
        await ctx.send(data_class.error["error"])
    else:
        await ctx.send(data_class.success["send"])
        for i in data_class.word["status"][game]:
            if i[:2] == "$!":
                word = data_class.status_data[game][i[2:]]
            else:
                word = i
                
            text += word
        await channel_obj.send(text)
        await ctx.send(data_class.success["send_end"])

# nickname change command
@bot.hybrid_command()
async def rec(ctx):
    nickname = f"{ctx.author.name}{data_class.word['record']}"
    if not ctx.author.nick:
        pass

    elif ctx.author.nick[:-data_class.rec_len] == ctx.author.name:
        nickname = None

    elif ctx.author.nick[-data_class.rec_len:] == data_class.word['record']:
        nickname = ctx.author.nick[:-data_class.rec_len]

    try:
        await ctx.author.edit(nick = nickname)
        await ctx.reply(data_class.success["chenged"])
    except:
        await ctx.reply(data_class.error["permission"])

# bot exit command. only use admin
@bot.command()
async def exit(ctx):
    if ctx.author.id in data_class.admin:
        print("exit")
        await ctx.reply("exit")
        await bot.close()
        await ctx.reply(data_class.error["feilure"])
    else:
        await ctx.reply(data_class.error["permisson"])

# reboot command. os reboot. only use admin
@bot.command()
async def reboot(ctx):
    if ctx.author.id in data_class.admin:
        print("reboot")
        await ctx.reply("reboot")
        subprocess.call("reboot")
        await bot.close()
        await ctx.reply(data_class.error["feilure"])
    else:
        await ctx.reply(data_class.error["permisson"])

with open("resource/token.json") as file:
    token = json.load(file)
bot.run(token["token"])