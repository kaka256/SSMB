import discord
from discord.ext import tasks, commands
import subprocess
import json
from ping3 import ping
import re

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="2jxg84G2CQ6PgYHtnBLn", intents=intents, help_command=None)

MESSAGE_FILE_PATH = "resource/message.json"
DATA_FILE_PATH = "resource/data.json"

def is_valid_ip(ip):
    ip_pattern = re.compile(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$")
    if ip_pattern.match(ip):
        return all(0 <= int(octet) <= 255 for octet in ip.split('.'))
    return False

class status_bot_data():
    def __init__(self):
        self.text = {}
        self.message_load()
        self.data_load()
        self.message_generate()
        self.last_status = {}
        for server in self.status_data:
            self.last_status[server] = None

    def message_load(self):
        with open(MESSAGE_FILE_PATH, encoding="utf-8_sig") as file:
            message = json.load(file)
            
        self.word = message["word"]
        self.messages = message["messages"]
        self.success = message["success"]
        self.error = message["error"]
        self.help = message["help"]
        self.rec_len = len(self.word["record"])

    def data_load(self):
        with open(DATA_FILE_PATH, encoding="utf-8_sig") as file:
            self.data_dict = json.load(file)
        self.admin = self.data_dict["admin"]
        self.status_data = self.data_dict["servers"]
        self.setting_guild = self.data_dict["setting_guild"]
    
    def data_write(self):
        with open("resource/data.json", mode="w", encoding="utf-8_sig") as file:
            json.dump(self.data_dict, file, indent=4)
            self.message_generate()

    def message_generate(self):
        server_dict = self.status_data
        for server in server_dict:
            text = ""
            for i in self.messages[server]:
                if i[:2] == "$!":
                    word = server_dict[server][i[2:]]
                else:
                    word = i
                text += str(word)
            self.text[server] = text

data_class = status_bot_data()

MY_GUILD_ID = discord.Object(id=data_class.setting_guild)

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')
    await bot.tree.sync()
    ping_check.start()

@tasks.loop(seconds=10.0)
async def ping_check():
    server_dict = data_class.status_data
    for server in server_dict:
        if not server_dict[server]["channel_id"]:
            continue

        channel_id = server_dict[server]["channel_id"]
        if not channel_id:
            continue

        server_ip = server_dict[server]["server_ip"]
        if not server_ip:
            continue
        
        responce = bool(ping(server_ip))
        if data_class.last_status[server] != responce:
            status_word = data_class.word["stop"]
            if responce:
                status_word = data_class.word["active"]

            server_dict[server]["status"] = status_word
            data_class.data_write()
            
            channel_obj = bot.get_channel(channel_id)
            message_obj = await channel_obj.fetch_message(server_dict[server]["message_id"])

            await message_obj.edit(content=data_class.text[server])
        data_class.last_status[server] = responce

# nickname change command
@bot.hybrid_command()
async def rec(ctx):
    nickname = f"{ctx.author.name}{data_class.word['record']}"
    
    if ctx.author.nick[:-data_class.rec_len] == ctx.author.name:
        nickname = None

    elif ctx.author.nick[-data_class.rec_len:] == data_class.word['record']:
        nickname = ctx.author.nick[:-data_class.rec_len]

    try:
        await ctx.author.edit(nick = nickname)
        await ctx.reply(data_class.success["changed"])
    except:
        await ctx.reply(data_class.error["permission"])

@bot.hybrid_command()
@discord.app_commands.guilds(MY_GUILD_ID)
async def help(ctx):
    text = ""
    for line in data_class.help:
        text += line
    await ctx.reply(text)

@bot.hybrid_command()
@discord.app_commands.guilds(MY_GUILD_ID)
async def sync(ctx, id):
    guild = discord.Object(id=id)
    await bot.tree.sync(guild=guild)
    await ctx.reply("reload")

# message.json reload
@bot.hybrid_command()
@discord.app_commands.guilds(MY_GUILD_ID)
async def message_reload(ctx):
    data_class.message_load()
    await ctx.send("reload")

# data.json reload
@bot.hybrid_command()
@discord.app_commands.guilds(MY_GUILD_ID)
async def data_reload(ctx):
    data_class.data_load()
    await ctx.send("reload")

# send server status
@bot.hybrid_command()
@discord.app_commands.guilds(MY_GUILD_ID)
async def send_message(ctx, channel_id, game):
    channel_id = int(channel_id)
    channel_obj = bot.get_channel(channel_id)
    game = game.lower()
    if not channel_obj or not game in data_class.messages:
        await ctx.send(data_class.error["error"])
    else:
        await ctx.send(data_class.success["send"])
        context = await channel_obj.send(data_class.text[game])
        data_dict = data_class.data_dict["servers"][game]
        data_dict["channel_id"] = channel_id
        data_dict["message_id"] = context.id
        data_class.data_write()
        await ctx.send(data_class.success["send_end"])

@bot.hybrid_command()
@discord.app_commands.guilds(MY_GUILD_ID)
async def edit_message(ctx, game, version=None, dlc=None, other=None):
    if not game in data_class.messages:
        await ctx.send(data_class.error["error"])
    else:
        data_dict = data_class.data_dict["servers"][game]
        if not dlc is None:
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
async def change_ip(ctx, game, ip):
    game = game.lower()
    if game not in data_class.status_data:
        await ctx.send(data_class.error["error"])
        return
    
    if is_valid_ip(ip):
        data_class.data_dict["servers"][game]["server_ip"] = ip
        data_class.data_write()
        await ctx.send(data_class.success["changed"])
    else:
        await ctx.send(data_class.error["value"])

@bot.hybrid_command()
@discord.app_commands.guilds(MY_GUILD_ID)
async def view_data(ctx):
    text = ""
    for server in data_class.status_data:
        text += f"\n{server}\n"
        for item in data_class.status_data[server]:
            text += f"{item}：{data_class.status_data[server][item]}\n"

    await ctx.send(text)

# bot exit command. only use admin
@bot.command()
async def exit(ctx):
    if ctx.author.id in data_class.admin:
        print("exit")   
        await ctx.reply("exit")
        await bot.close()
        await ctx.reply(data_class.error["failure"])
    else:
        await ctx.reply(data_class.error["permission"])

# reboot command. os reboot. only use admin
@bot.command()
async def reboot(ctx):
    if ctx.author.id in data_class.admin:
        print("reboot")
        await ctx.reply("reboot")
        subprocess.call("reboot")
        await bot.close()
        await ctx.reply(data_class.error["failure"])
    else:
        await ctx.reply(data_class.error["permission"])

with open("resource/token.json") as file:
    token = json.load(file)
bot.run(token["token"])