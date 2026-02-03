import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os
import time

load_dotenv()

token = os.getenv('DISCORD_TOKEN')
jail_channel_id = 0
jail_name = "Strafkamp voor Bas"

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

secret_role = "Gamer"
class Prisoner:
    name = ''
    origin = ''
    timeout = 0
    
    def __init__(self, name, origin, timeout):
        self.name = name
        self.origin = origin
        self.timeout = int(time.time()) + timeout

jail_list = [Prisoner]

@bot.event
async def on_ready():
    print(f"We are ready to go in, {bot.user.name}")
    

@bot.command()
async def jail(ctx, *, msg):
    msgs = str(msg).split()

    user = await bot.fetch_user(msgs[0].removeprefix("<@").removesuffix(">"))
    #clear list of previous sentences
    list = [j for j in jail_list if j.name == user]
    for i in list :
        jail_list.remove(i)

    #add new sentence to list
    jail_list.append(Prisoner(user,"",int(msgs[1])))

    #get channel used for the jail
    global jail_channel_id
    channel = discord.utils.get(ctx.guild.channels, name=jail_name)
    jail_channel_id = channel.id
    channel = bot.get_channel(jail_channel_id)
    print(channel)

    #send message in chat
    await ctx.send(f"{user.display_name} has been jailed for {msgs[1]} seconds")

    #move the actual user to the jail channel
    members = bot.get_all_members()
    for m in members:
        if m.id == user.id :
            await m.move_to(channel)


@bot.command()
async def free(ctx, *, msg):
    msgs = str(msg).split()
    user = await bot.fetch_user(msgs[0].removeprefix("<@").removesuffix(">"))
    list = [j for j in jail_list if j.name == user]
    for i in list :
        jail_list.remove(i)

@bot.command()
async def renamejail(ctx, *, msg):
    global jail_name
    jail_name = msg
    await ctx.send(f"Jail has been renamed to {msg}")


@bot.event
async def on_voice_state_update(member, before, after):
    list = [j for j in jail_list if j.name == member]
    for l in list :
        if l.timeout <= time.time() : list.remove(l)
    if len(list) > 0 and after.channel.id != before.channel.id and after.channel.id != jail_channel_id:
        channel = bot.get_channel(jail_channel_id)
        await member.move_to(channel)

bot.run(token, log_handler=handler, log_level=logging.DEBUG)
