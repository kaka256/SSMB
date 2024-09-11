import discord
from discord.ext import commands
import subprocess
import json

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

admin = 378480271965683713 # kaka_256 user_id

class bot_data():
    def __init__(self):
        self.message_load()
        with open("data.json", encoding="utf-8_sig") as file:
            self.data = json.load(file)

    def message_load(self):
        with open("message.json", encoding="utf-8_sig") as file:
            message = json.load(file)
            
        self.word = message["word"]
        self.success = message["success"]
        self.error = message["error"]
        self.rec_len = len(self.word["record"])

data_class = bot_data()

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')
    await bot.tree.sync()

@bot.command()
async def message_reload(ctx):
    data_class.message_load()
    await ctx.send("reload")

# send server status
@bot.hybrid_command()
async def send_message(ctx, channel_id, game):
    channel_obj = bot.get_channel(int(channel_id))
    game = game.lower()
    text = ""
    if not channel_obj:
        await ctx.send("error")
    else:
        await ctx.send(data_class.success["send"])
        for i in data_class.word["status"][game]:
            text += i
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
@bot.hybrid_command()
async def exit(ctx):
    if ctx.author.id == admin:
        print("exit")
        await ctx.reply("exit")
        await bot.close()
        await ctx.reply(data_class.error["feilure"])
    else:
        await ctx.reply(data_class.error["permisson"])

# reboot command. os reboot. only use admin
@bot.hybrid_command()
async def reboot(ctx):
    if ctx.author.id == admin:
        print("reboot")
        await ctx.reply("reboot")
        subprocess.call("reboot")
        await bot.close()
        await ctx.reply(data_class.error["feilure"])
    else:
        await ctx.reply(data_class.error["permisson"])

with open("token.json") as file:
    token = json.load(file)
bot.run(token["token"])