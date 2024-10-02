import discord, dotenv, os
from discord.ext import commands, tasks
from dotenv import load_dotenv
from discord.ui import Button, View
from discord import app_commands, ui
from src.bot import LFGBot


load_dotenv()
BOT_TOKEN = os.environ.get('BOT_TOKEN')
#RIOT_KEY = os.environ.get('RIOT_KEY')

if BOT_TOKEN:
    print("BOT_TOKEN loaded successfully")
else:
    print("BOT_TOKEN not found in env vars")

bot = LFGBot()

if __name__ == "__main__":
    bot.run(BOT_TOKEN)

