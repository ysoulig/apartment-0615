import os
import discord
from discord import app_commands


class ApartmentBot(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        super().__init__(intents=intents)

        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        await self.tree.sync()


bot = ApartmentBot()


@bot.event
async def on_ready():
    print(f"🏠 apartment-0615 is online!")
    print(f"Logged in as {bot.user}")


@bot.tree.command(name="ping", description="Check if apartment-0615 is alive!")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message(
        "🏠 apartment-0615 is alive!"
    )


bot.run(os.environ["DISCORD_TOKEN"])
