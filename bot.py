import os
import asyncio
import discord
from discord.ext import tasks
from aiohttp import ClientSession, ClientTimeout

# Obsługa obu metod podawania tokenu
if "DISCORD_TOKEN" in os.environ:
    TOKEN = os.environ["DISCORD_TOKEN"].strip()
else:
    TOKEN = ".".join([
        os.environ["TOKEN_A"].strip(),
        os.environ["TOKEN_B"].strip(),
        os.environ["TOKEN_C"].strip(),
    ])

MC_IP = os.environ["MC_IP"]
MC_PORT = os.environ.get("MC_PORT", "25565")
API_URL = f"https://mcapi.us/server/status?ip={MC_IP}&port={MC_PORT}"

intents = discord.Intents.default()
client = discord.Client(intents=intents)


@tasks.loop(seconds=5)
async def update_status():
    try:
        async with ClientSession() as session:
            async with session.get(API_URL, timeout=ClientTimeout(total=10)) as resp:
                data = await resp.json()

        if data.get("online"):
            players = data.get("players", {}).get("now", 0)
            print(f"MC ok: {players} online")
            activity = discord.Game(name=f"🎮 {players} online")
        else:
            print("MC: offline")
            activity = discord.Game(name="🔴 Serwer offline")

    except Exception as e:
        print(f"MC error ({type(e).__name__}): {e}")
        activity = discord.Game(name="🔴 Serwer offline")

    await client.change_presence(activity=activity)


@client.event
async def on_ready():
    print(f"Bot zalogowany jako {client.user}")
    print(f"API: {API_URL}")
    update_status.start()


client.run(TOKEN)
