import os
import asyncio
import discord
from discord.ext import tasks
from mcstatus import JavaServer
from aiohttp import web

TOKEN = ".".join([
    os.environ["TOKEN_A"].strip(),
    os.environ["TOKEN_B"].strip(),
    os.environ["TOKEN_C"].strip(),
])
MC_IP = os.environ["MC_IP"]
MC_PORT = int(os.environ.get("MC_PORT", 25565))
PORT = int(os.environ.get("PORT", 0))

intents = discord.Intents.default()
client = discord.Client(intents=intents)


@tasks.loop(seconds=5)
async def update_status():
    try:
        server = JavaServer(MC_IP, MC_PORT)
        status = await asyncio.wait_for(server.async_status(), timeout=5.0)
        players = status.players.online
        activity = discord.Game(name=f"🎮 {players} online")
    except Exception:
        activity = discord.Game(name="🔴 Serwer offline")

    await client.change_presence(activity=activity)


@client.event
async def on_ready():
    print(f"Bot zalogowany jako {client.user}")
    update_status.start()


async def health(request):
    return web.Response(text="OK")


async def start_health_server():
    app = web.Application()
    app.router.add_get("/health", health)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()
    print(f"Health server uruchomiony na porcie {PORT}")


async def main():
    if PORT > 0:
        await start_health_server()
    await client.start(TOKEN)


asyncio.run(main())
