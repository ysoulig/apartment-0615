import os
import json
import random
import time
from collections import Counter

import discord
from discord import app_commands


# -------------------------
# Settings
# -------------------------

DROP_COOLDOWN = 10 * 60
CLAIM_COOLDOWN = 10 * 60


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
# Save user database
# -------------------------

def save_users():
    with open("users.json", "w", encoding="utf-8") as file:
        json.dump(
            {"users": users},
            file,
            indent=2,
            ensure_ascii=False
        )


# -------------------------
# Time helpers
# -------------------------

def get_remaining_time(last_used, cooldown):
    remaining = cooldown - (time.time() - last_used)

    if remaining <= 0:
        return 0

    return int(remaining)


def format_time(seconds):
    minutes = seconds // 60
    seconds = seconds % 60

    if minutes > 0:
        return f"{minutes}m {seconds}s"

    return f"{seconds}s"


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
# User setup
# -------------------------

def get_user(user_id):
    user_id = str(user_id)

    if user_id not in users:
        users[user_id] = {
            "cards": [],
            "last_drop": 0,
            "last_claim": 0
        }

        save_users()

    return users[user_id]


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

    user = get_user(interaction.user.id)

    collection = user["cards"]

    if len(collection) == 0:
        await interaction.response.send_message(
            "📚 Your collection is empty!\n"
            "Use `/drop` to start collecting cards."
        )
        return

    card_counts = Counter(collection)

    message = "📚 **Your Collection**\n\n"

    for card_id, amount in card_counts.items():
        message += f"🃏 **{card_id}** ×{amount}\n"

    message += f"\n**Total cards:** {len(collection)}"

    await interaction.response.send_message(message)


# -------------------------
# Card drop buttons
# -------------------------

class CardDropView(discord.ui.View):

    def __init__(self, dropped_cards, dropper_id):
        super().__init__(timeout=300)

        self.dropped_cards = dropped_cards
        self.dropper_id = dropper_id
        self.claimed_cards = set()
        self.first_pick_done = False

        for number in range(3):
            button = discord.ui.Button(
                label=f"Card {number + 1}",
                style=discord.ButtonStyle.primary,
                custom_id=f"card_drop_{number}"
            )

            button.callback = self.make_callback(number)
            self.add_item(button)

    def make_callback(self, number):

        async def callback(interaction: discord.Interaction):

            user_id = interaction.user.id
            card = self.dropped_cards[number]
            card_id = card["id"]

            # Card already claimed
            if number in self.claimed_cards:
                await interaction.response.send_message(
                    "❌ That card has already been claimed!",
                    ephemeral=True
                )
                return

            # Dropper gets first pick
            if not self.first_pick_done:

                if user_id != self.dropper_id:
                    await interaction.response.send_message(
                        "⏳ The person who dropped these cards gets first pick!",
                        ephemeral=True
                    )
                    return

            # After first pick, check claim cooldown
            else:

                user = get_user(user_id)

                remaining = get_remaining_time(
                    user["last_claim"],
                    CLAIM_COOLDOWN
                )

                if remaining > 0:
                    await interaction.response.send_message(
                        f"⏳ You're on claim cooldown!\n"
                        f"Try again in **{format_time(remaining)}**.",
                        ephemeral=True
                    )
                    return

            # Make sure user exists
            user = get_user(user_id)

            # Give card
            user["cards"].append(card_id)

            # First pick is not a claim cooldown
            if self.first_pick_done:
                user["last_claim"] = time.time()

            self.first_pick_done = True
            self.claimed_cards.add(number)

            save_users()

            # Disable claimed button
            for child in self.children:
                if isinstance(child, discord.ui.Button):

                    if child.custom_id == f"card_drop_{number}":
                        child.disabled = True
                        child.label = "CLAIMED"
                        child.style = discord.ButtonStyle.secondary

            await interaction.response.edit_message(
                content=(
                    f"🃏 **CARD DROP**\n\n"
                    f"🎉 {interaction.user.mention} claimed "
                    f"**{card_id}**!\n\n"
                    f"Remaining cards can be claimed by other users."
                ),
                view=self
            )

            if len(self.claimed_cards) == 3:
                self.stop()

        return callback


# -------------------------
# /drop
# -------------------------

@bot.tree.command(
    name="drop",
    description="Drop three cards for everyone to claim!"
)
async def drop(interaction: discord.Interaction):

    user = get_user(interaction.user.id)

    remaining = get_remaining_time(
        user["last_drop"],
        DROP_COOLDOWN
    )

    if remaining > 0:
        await interaction.response.send_message(
            f"⏳ You can't drop yet!\n"
            f"Try again in **{format_time(remaining)}**.",
            ephemeral=True
        )
        return

    if len(cards) < 3:
        await interaction.response.send_message(
            "❌ There aren't enough cards for a drop yet!"
        )
        return

    dropped_cards = random.sample(cards, 3)

    user["last_drop"] = time.time()

    save_users()

    view = CardDropView(
        dropped_cards,
        interaction.user.id
    )

    message = (
        "🃏 **CARD DROP!**\n\n"
        f"👑 Dropped by {interaction.user.mention}\n\n"
        "The dropper gets **first pick**!\n"
        "After that, anyone can claim the remaining cards.\n\n"
    )

    for number, card in enumerate(dropped_cards, start=1):
        message += (
            f"**Card {number}**\n"
            f"`{card['id']}` • "
            f"{card['group']} — {card['member']}\n"
            f"💿 {card['era']} • ⭐ Tier {card['tier']}\n\n"
        )

    await interaction.response.send_message(
        message,
        view=view
    )


# -------------------------
# Start bot
# -------------------------

bot.run(os.environ["DISCORD_TOKEN"])
