from pyrogram import Client, errors
import pyrogram.raw.types as pyrogram_raw_types

# PyTgCalls 2.3.3 imports Telegram's inputGroupCallSlug constructor.
# Some Pyrogram-compatible forks do not expose this newer raw type.
# The relay only uses normal group voice-chat calls, so provide a minimal
# compatibility class so PyTgCalls can import successfully.
if not hasattr(pyrogram_raw_types, "InputGroupCallSlug"):
    class InputGroupCallSlug:
        def __init__(self, slug: str):
            self.slug = slug

        def __repr__(self):
            return f"InputGroupCallSlug(slug={self.slug!r})"

    pyrogram_raw_types.InputGroupCallSlug = InputGroupCallSlug

import pyrogram.errors as pyrogram_errors

# PyTgCalls 2.3.3 expects newer Telegram raw types than official Pyrogram 2.0.106.
# Pyrofork provides the compatible pyrogram import namespace and raw TL types.

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
