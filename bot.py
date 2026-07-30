import os
import discord
from discord.ext import commands

# Bot permissions
intents = discord.Intents.default()

# Create the bot
bot = commands.Bot(
    command_prefix="!",
    intents=intents
)


@bot.event
async def on_ready():
    print("apartment-0615 is online!")
    print(f"Logged in as {bot.user}")


@bot.command()
async def ping(ctx):
    await ctx.send("🏠 apartment-0615 is alive!")


# Start the bot
bot.run(os.environ["DISCORD_TOKEN"])
