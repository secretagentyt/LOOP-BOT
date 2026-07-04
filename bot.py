import os
import discord
from discord.ext import tasks
from mcstatus import JavaServer

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
MC_PORT = int(os.environ.get("MC_PORT", "25565"))

server = JavaServer.lookup(f"{MC_IP}:{MC_PORT}")

intents = discord.Intents.default()
client = discord.Client(intents=intents)


@tasks.loop(seconds=5)
async def update_status():
    try:
        status = await server.async_status()
        players = status.players.online
        print(f"MC ok: {players} online")
        activity = discord.Game(name=f"🎮 {players} online")
    except Exception as e:
        print(f"MC offline ({type(e).__name__}): {e}")
        activity = discord.Game(name="🔴 Serwer offline")

    await client.change_presence(activity=activity)


@client.event
async def on_ready():
    print(f"Bot zalogowany jako {client.user}")
    print(f"Serwer MC: {MC_IP}:{MC_PORT}")
    update_status.start()


client.run(TOKEN)
