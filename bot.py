# Imports
import discord
from discord.ext import commands
import datetime
import json
import tweepy
import os
from tweepy import HTTPException
from pymongo import MongoClient

# Importing Database
cluster = MongoClient(os.environ["MONGO_API"])

db = cluster["discord"]
collection = db["config"]

# Discord Intents
intents = discord.Intents.all()
intents.members = True

client = commands.Bot(intents=intents, command_prefix='.')

# Getting config datas
config = collection.find_one({"_id": 0})  # If you stored your keys on MONGODB

# conf = open("./config/config.json")   # If you are using config.json then comment the above line and uncomment these two lines
# config = json.load(conf)

# Twitter auth
auth = tweepy.OAuth1UserHandler(config['twitter_credentials']['consumer_key'],
                                config['twitter_credentials']['consumer_secret'],
                                config['twitter_credentials']['access_token'],
                                config['twitter_credentials']['access_token_secret'])

api = tweepy.API(auth, wait_on_rate_limit=True)


# Discord Commands
@client.command()
async def add(ctx, username):
    try:
        datas = collection.find_one({"_id": 0})
        if username in datas['victims']:
            await ctx.send("User is already on tracklist")
            return
        user = api.get_user(screen_name=username)
        datas['victims'].append(username)
        collection.delete_one({"_id": 0})
        collection.insert_one(datas)
        await ctx.send(f"{username} has been added successfully")
    except HTTPException as e:
        await ctx.send("User not found")


@client.command()
async def remove(ctx, username):
    datas = collection.find_one({"_id": 0})
    if username in datas['victims']:
        datas['victims'].remove(username)
        collection.delete_one({"_id": 0})
        collection.insert_one(datas)
        await ctx.send(f"{username} has been removed successfully")
    else:
        await ctx.send(f"{username} was never added")

@client.command()
async def showtracks(ctx):
    datas = collection.find_one({"_id": 0})
    victims = datas['victims']
    victims = [f'{count + 1}. {i}' for count, i in enumerate(victims)]
    victims = '\n'.join(victims)
    embed = discord.Embed(title='Tracked Users', colour=discord.Colour.blue())
    embed.set_thumbnail(url="http://clipart-library.com/new_gallery/70-700616_cool-circle-designs-png-435999.png")
    embed.add_field(name='\u200b', value=victims)
    embed.timestamp = datetime.datetime.utcnow()
    embed.set_footer(text='\u200b')
    await ctx.send(embed=embed)

    
@client.command()
async def addwallet(ctx, wallet, nickname):
    datas = collection.find_one({"_id": 0})
    if wallet in datas['wallets']:
        await ctx.send("User is already on tracklist")
        return
    if len(wallet) != 42:
        await ctx.send("invalid wallet")
        return
    datas['wallets'][wallet.lower()] = nickname.lower()
    collection.delete_one({"_id": 0})
    collection.insert_one(datas)
    await ctx.send(f"{wallet} has been added successfully")


@client.command()
async def removewallet(ctx, iden):
    datas = collection.find_one({"_id": 0})
    iden = iden.lower()
    if iden in datas['wallets'].keys():
        del datas['wallets'][iden]
        collection.replace_one({"_id": 0}, datas)
        await ctx.send(f"{iden} has been removed successfully")
    elif iden in datas['wallets'].values():
        key = [k for k, v in datas['wallets'].items() if v == iden][0]
        del datas['wallets'][key]
        collection.replace_one({"_id": 0}, datas)
        await ctx.send(f"{iden} has been removed successfully")
    else:
        await ctx.send(f"{iden} was never added")

@client.command()
async def showwallets(ctx):
    wallets = collection.find_one({"_id": 0})["wallets"]
    temp = ""
    for key, value in wallets.items():
        temp += f"{value} : {key}\n"
    await ctx.send(temp)
    
client.run(os.environ["DISCORD_TOKEN"])
