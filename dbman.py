import aiosqlite
import asyncio

from main import bolb

async def execute(statement: str, args=None):
    db = await aiosqlite.connect("bolb.db")
    await db.execute(statement, args if args else ())
    await db.commit()
    await db.close()

async def make():
    await execute("CREATE TABLE IF NOT EXISTS bolb (user_id INTEGER PRIMARY KEY, bolbs INTEGER, daily_cd INTEGER, weekly_cd INTEGER)")

async def put():
    await execute("INSERT INTO bolb (user_id, bolbs, daily_cd, weekly_cd) VALUES (?, ?, ?, ?)", (2, 3, 4, 5))

async def select():
    db = await aiosqlite.connect("bolb.db")
    x = await db.execute("SELECT daily_cd from bolb WHERE user_id = ?", (2, ))
    y = await x.fetchone()
    print(y)
    print(type(y))

async def bolb_users():
    db = await aiosqlite.connect("bolb.db")
    bolb_users = await db.execute("SELECT user_id FROM bolb")
    bolb_users = await bolb_users.fetchall()
    print(bolb_users)


asyncio.run(bolb_users())