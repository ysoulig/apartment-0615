import os
import json
import random

import discord
from discord import app_commands


# -------------------------
# Load card database
# -------------------------

with open("cards.json", "r", encoding="utf-8") as file:
    card_data = json.load(file)

cards = card_data["cards"]


# -------------------------
# Load group database
# -------------------------

with open("groups.json", "r", encoding="utf-8") as file:
    group_data = json.load(file)

groups = group_data["groups"]


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
    print(f"Loaded {len(groups)} groups.")


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
    description="See how many cards are in the database."
)
async def cards_command(interaction: discord.Interaction):
    await interaction.response.send_message(
        f"🃏 The database currently contains **{len(cards)} cards**."
    )


# -------------------------
# /drop
# -------------------------

@bot.tree.command(
    name="drop",
    description="Drop three random cards!"
)
async def drop(interaction: discord.Interaction):

    if len(cards) < 3:
        await interaction.response.send_message(
            "❌ There aren't enough cards in the database yet!"
        )
        return

    dropped_cards = random.sample(cards, 3)

    message = "🃏 **A CARD DROP!**\n\n"

    for card in dropped_cards:
        message += (
            f"**{card['id']}**\n"
            f"{card['group']} — {card['member']}\n"
            f"Tier {card['tier']} • {card['era']}\n\n"
        )

    await interaction.response.send_message(message)


# -------------------------
# Start bot
# -------------------------

bot.run(os.environ["DISCORD_TOKEN"])
