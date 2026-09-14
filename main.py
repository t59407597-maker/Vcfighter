from pyrogram import Client, errors
import pyrogram.errors as pyrogram_errors

# Compatibility layer: py-tgcalls imports these legacy Pyrogram names.
# Define them BEFORE relay.commands imports PyTgCalls.
if not hasattr(pyrogram_errors, "GroupcallForbidden"):
    if hasattr(pyrogram_errors, "GroupCallForbidden"):
        pyrogram_errors.GroupcallForbidden = pyrogram_errors.GroupCallForbidden
    else:
        class GroupcallForbidden(pyrogram_errors.BadRequest):
            pass
        pyrogram_errors.GroupcallForbidden = GroupcallForbidden

if not hasattr(pyrogram_errors, "GroupcallInvalid"):
    if hasattr(pyrogram_errors, "GroupCallInvalid"):
        pyrogram_errors.GroupcallInvalid = pyrogram_errors.GroupCallInvalid
    else:
        class GroupcallInvalid(pyrogram_errors.BadRequest):
            pass
        pyrogram_errors.GroupcallInvalid = GroupcallInvalid

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
