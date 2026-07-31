import os
import json
import discord
from discord import app_commands


# -------------------------
# Load card database
# -------------------------

with open("cards.json", "r", encoding="utf-8") as file:
    card_data = json.load(file)

cards = card_data["cards"]


# -------------------------
# Create bot
# -------------------------

class ApartmentBot(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        super().__init__(intents=intents)

        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        await self.tree.sync()


bot = ApartmentBot()


# -------------------------
# Bot startup
# -------------------------

@bot.event
async def on_ready():
    print("🏠 apartment-0615 is online!")
    print(f"Logged in as {bot.user}")
    print(f"Loaded {len(cards)} cards.")


# -------------------------
# /ping
# -------------------------

@bot.tree.command(
    name="ping",
    description="Check if apartment-0615 is alive!"
)
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message(
        "🏠 apartment-0615 is alive!"
    )


# -------------------------
# /cards
# -------------------------

@bot.tree.command(
    name="cards",
    description="See how many cards are currently in the database."
)
async def cards_command(interaction: discord.Interaction):
    await interaction.response.send_message(
        f"🃏 apartment-0615 currently has **{len(cards)} cards**!"
    )


# -------------------------
# Start bot
# -------------------------

bot.run(os.environ["DISCORD_TOKEN"])
