import logging
from pyrogram import filters
from config import CONTROL_GROUP_ID, DEFAULT_VOLUME
from relay import state
from relay.vc_bridge import VCBridge

log = logging.getLogger(__name__)
bridge = None

def register(app):
    global bridge
    bridge = VCBridge(app)
    state.volume = DEFAULT_VOLUME

    @app.on_message(filters.command("connect") & filters.chat(CONTROL_GROUP_ID))
    async def connect(_, message):
        if len(message.command) < 2:
            return await message.reply_text("Usage: /connect <target_group_id>")
        try:
            target = int(message.command[1])
        except ValueError:
            return await message.reply_text("❌ Target group ID must be a number.")
        try:
            await bridge.start(message.chat.id, target)
            await message.reply_text(f"🔗 Connected → `{target}`")
        except Exception as exc:
            log.exception("Unable to connect relay")
            await message.reply_text(f"❌ Relay start failed: `{type(exc).__name__}: {exc}`")

    @app.on_message(filters.command("volume") & filters.chat(CONTROL_GROUP_ID))
    async def volume(_, message):
        if len(message.command) < 2:
            return await message.reply_text("Usage: /volume <0-300>")
        try:
            percent = int(message.command[1])
        except ValueError:
            return await message.reply_text("❌ Volume must be a number from 0 to 300.")
        percent = max(0, min(300, percent))
        state.volume = percent / 100.0
        await message.reply_text(f"🔊 Volume = {percent}%")

    @app.on_message(filters.command("stop") & filters.chat(CONTROL_GROUP_ID))
    async def stop(_, message):
        try:
            await bridge.stop()
            await message.reply_text("⛔ Relay stopped")
        except Exception as exc:
            log.exception("Unable to stop relay")
            await message.reply_text(f"❌ Stop failed: `{type(exc).__name__}: {exc}`")
