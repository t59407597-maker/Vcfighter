from pyrogram import Client, errors
from pyrogram.session import StringSession
from config import API_HASH, API_ID, SESSION_NAME, SESSION_STRING
from relay.commands import register

if SESSION_STRING:
    app = Client(StringSession(SESSION_STRING), api_id=API_ID, api_hash=API_HASH)
else:
    app = Client(SESSION_NAME, api_id=API_ID, api_hash=API_HASH)

register(app)
print("🔊 VC Relay Bot started", flush=True)

try:
    app.run()
except errors.BadRequest as exc:
    print(f"Telegram startup error: {exc}", flush=True)
    raise
