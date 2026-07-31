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
# Load user database
# -------------------------

with open("users.json", "r", encoding="utf-8") as file:
    user_data = json.load(file)

users = user_data["users"]


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
    print(f"Loaded {len(users)} users.")


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
    description="See the cards currently in the database."
)
async def cards_command(interaction: discord.Interaction):

    message = "🃏 **Cards currently in apartment-0615:**\n\n"

    for card in cards:
        message += (
            f"**{card['id']}** — "
            f"{card['group']} • {card['member']} • "
            f"{card['era']} • Tier {card['tier']}\n"
        )

    await interaction.response.send_message(message)


# -------------------------
# /collection
# -------------------------

@bot.tree.command(
    name="collection",
    description="View your card collection."
)
async def collection(interaction: discord.Interaction):

    user_id = str(interaction.user.id)

    if user_id not in users:
        users[user_id] = {
            "cards": []
        }

    collection = users[user_id]["cards"]

    if len(collection) == 0:
        await interaction.response.send_message(
            "📚 Your collection is empty!\n"
            "Use `/drop` to start collecting cards."
        )
        return

    message = "📚 **Your Collection**\n\n"

    for card_id in collection:
        message += f"🃏 {card_id}\n"

    await interaction.response.send_message(message)


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
            "❌ There aren't enough cards for a drop yet!"
        )
        return

    dropped_cards = random.sample(cards, 3)

    message = "🃏 **CARD DROP**\n\n"

    for number, card in enumerate(dropped_cards, start=1):
        message += (
            f"**{number}. {card['id']}**\n"
            f"👤 {card['group']} — {card['member']}\n"
            f"💿 {card['era']}\n"
            f"⭐ Tier {card['tier']}\n\n"
        )

    await interaction.response.send_message(message)


# -------------------------
# Start bot
# -------------------------

bot.run(os.environ["DISCORD_TOKEN"])
