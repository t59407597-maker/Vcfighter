from pyrogram import Client, errors
import pyrogram.errors as pyrogram_errors

# py-tgcalls 2.3.3 imports the legacy spelling `GroupcallForbidden`,
# while Pyrogram 2.0.106 exposes `GroupCallForbidden`.
# Provide the compatibility alias before PyTgCalls is imported.
if not hasattr(pyrogram_errors, "GroupcallForbidden") and hasattr(pyrogram_errors, "GroupCallForbidden"):
    pyrogram_errors.GroupcallForbidden = pyrogram_errors.GroupCallForbidden

from config import API_HASH, API_ID, SESSION_NAME, SESSION_STRING
from relay.commands import register


if SESSION_STRING:
    app = Client(
        SESSION_NAME,
        api_id=API_ID,
        api_hash=API_HASH,
        session_string=SESSION_STRING,
    )
else:
    app = Client(
        SESSION_NAME,
        api_id=API_ID,
        api_hash=API_HASH,
    )

register(app)
print("🔊 VC Relay Bot started", flush=True)

try:
    app.run()
except errors.BadRequest as exc:
    print(f"Telegram startup error: {exc}", flush=True)
    raise
