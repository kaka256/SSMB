import discord
from discord.ext import tasks, commands
import subprocess
import json
from ping3 import ping

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

class status_bot_data():
    def __init__(self):
        self.message_load()
        self.data_load()
        self.last_status = False

    def message_load(self):
        with open("resource/message.json", encoding="utf-8_sig") as file:
            message = json.load(file)
            
        self.word = message["word"]
        self.success = message["success"]
        self.error = message["error"]
        self.rec_len = len(self.word["record"])

    def data_load(self):
        with open("resource/data.json", encoding="utf-8_sig") as file:
            self.data_dict = json.load(file)
        self.admin = self.data_dict["admin"]
        self.status_data = self.data_dict["status"]
    
    def data_write(self, game, status=None, channle_id=None, message_id=None, version=None, dlc=None):
        with open("resource/data.json", mode="w", encoding="utf-8_sig") as file:
            if not status is None:
                self.data_dict["status"][game]["status"] = status
            if not channle_id is None:
                self.data_dict["status"][game]["channel_id"] = channle_id
            if not message_id is None:
                self.data_dict["status"][game]["message_id"] = message_id
            if not version is None:
                self.data_dict["status"][game]["ver"] = version
            if not version is None:
                self.data_dict["status"][game]["dlc"] = dlc
            json.dump(self.data_dict, file, indent=4)

data_class = status_bot_data()

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')
    await bot.tree.sync()
    ping_chack.start()

@tasks.loop(seconds=10.0)
async def ping_chack():
    data_dict = data_class.data_dict["status"]
    responce = ping(data_class.data_dict["server_ip"])
    if data_class.last_status == (not responce):
        status_word = data_class.word["active"]
        if not responce:
            status_word = data_class.word["stop"]
        for game in data_dict:
            data_dict[game]["status"] = status_word
            channel_id = data_dict[game]["channel_id"]
            data_class.data_write(game=game, status=status_word)

            new_data = {"status": status_word , "ver": data_dict[game]["ver"], "dlc": data_dict[game]["dlc"]}
            text = ""
            for i in data_class.word["status"][game]:
                if i[:2] == "$!":
                    word = new_data[i[2:]]
                else:
                    word = i
                    
                text += word
            channel_obj = bot.get_channel(channel_id)
            message_obj = await channel_obj.fetch_message(data_dict[game]["message_id"])
            await message_obj.edit(content=text)

    data_class.last_status = not responce
    print(data_dict)

# message.json reload
@bot.command()
async def message_reload(ctx):
    data_class.message_load()
    await ctx.send("reload")

# data.json reload
@bot.command()
async def data_reload(ctx):
    data_class.data_load()
    await ctx.send("reload")

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

# send server status
@bot.command()
async def send_message(ctx, channel_id, game):
    channel_id = int(channel_id)
    channel_obj = bot.get_channel(channel_id)
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
        context = await channel_obj.send(text)
        data_class.data_write(game, channle_id=channel_id, message_id=context.id)
        await ctx.send(data_class.success["send_end"])

@bot.command()
async def edit_message(ctx, game, version, dlc=None):
    if not game in data_class.word["status"]:
        await ctx.send(data_class.error["error"])
    else:
        data_dict = data_class.data_dict["status"][game]
        new_data = {"status":data_dict["status"] , "ver": version, "dlc": dlc}
        text = ""
        for i in data_class.word["status"][game]:
            if i[:2] == "$!":
                word = new_data[i[2:]]
            else:
                word = i
                
            text += word

        channel_obj = bot.get_channel(data_dict["channel_id"])
        message_obj = await channel_obj.fetch_message(data_dict["message_id"])
        data_class.data_write(game=game, version=version, dlc=dlc)
        await message_obj.edit(content=text)
        await ctx.send("edit")

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