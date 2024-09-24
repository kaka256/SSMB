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
        self.text = {}
        self.message_load()
        self.data_load()
        self.message_generate()
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
        self.setting_guilds = self.data_dict["setting_guilds"]
    
    def data_write(self):
        with open("resource/data.json", mode="w", encoding="utf-8_sig") as file:
            json.dump(self.data_dict, file, indent=4)
            self.message_generate()

    def message_generate(self):
        temp_dict = self.data_dict["status"]
        for game in temp_dict:
            text = ""
            for i in self.word["status"][game]:
                if i[:2] == "$!":
                    word = temp_dict[game][i[2:]]
                else:
                    word = i
                text += str(word)
            self.text[game] = text

data_class = status_bot_data()

MY_GUILD_ID = discord.Object(id=data_class.setting_guilds)

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')
    await bot.tree.sync()
    ping_chack.start()

@tasks.loop(seconds=10.0)
async def ping_chack():
    data_dict = data_class.data_dict["status"]
    for game in data_dict:
        if not data_dict[game]["channel_id"]:
            return
    responce = ping(data_class.data_dict["server_ip"])
    if data_class.last_status != (not responce):
        status_word = data_class.word["active"]
        if not responce:
            status_word = data_class.word["stop"]
        for game in data_dict:
            data_dict[game]["status"] = status_word
            data_class.data_write()
            
            channel_id = data_dict[game]["channel_id"]
            channel_obj = bot.get_channel(channel_id)
            message_obj = await channel_obj.fetch_message(data_dict[game]["message_id"])

            await message_obj.edit(content=data_class.text[game])
        print(data_dict)
    data_class.last_status = not responce

# test command
@bot.command()
async def sync(ctx, id):
    guild = discord.Object(id=id)
    await bot.tree.sync(guild=guild)
    await ctx.reply("reload")

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
        await ctx.reply(data_class.success["changed"])
    except:
        await ctx.reply(data_class.error["permission"])

# send server status
@bot.hybrid_command()
@discord.app_commands.guilds(MY_GUILD_ID)
async def send_message(ctx, channel_id, game):
    channel_id = int(channel_id)
    channel_obj = bot.get_channel(channel_id)
    game = game.lower()
    text = ""
    if not channel_obj or not game in data_class.word["status"]:
        await ctx.send(data_class.error["error"])
    else:
        await ctx.send(data_class.success["send"])
        context = await channel_obj.send(data_class.text[game])
        data_dict = data_class.data_dict["status"][game]
        data_dict["channel_id"] = channel_id
        data_dict["message_id"] = context.id
        data_class.data_write()
        await ctx.send(data_class.success["send_end"])

@bot.hybrid_command()
@discord.app_commands.guilds(MY_GUILD_ID)
async def edit_message(ctx, game, version, dlc=None, other=None):
    if not game in data_class.word["status"]:
        await ctx.send(data_class.error["error"])
    else:
        data_dict = data_class.data_dict["status"][game]
        data_dict["ver"] = version
        if not dlc is None:
            data_dict["dlc"] = dlc
        if not other is None:
            data_dict["other"] = other
        data_class.data_write()

        channel_obj = bot.get_channel(data_dict["channel_id"])
        message_obj = await channel_obj.fetch_message(data_dict["message_id"])

        await message_obj.edit(content=data_class.text[game])
        await ctx.send(data_class.success["changed"])

@bot.hybrid_command()
@discord.app_commands.guilds(MY_GUILD_ID)
async def change_ip(ctx, ip):
    data_class.data_dict["server_ip"] = ip
    data_class.data_write()
    await ctx.send(data_class.success["changed"])
    pass

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