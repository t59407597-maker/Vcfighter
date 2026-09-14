import logging

from pyrogram import filters

from config import CONTROL_GROUP_ID, DEFAULT_VOLUME
from relay import state
from relay.vc_bridge import VCBridge

log = logging.getLogger(__name__)
bridge = None


def _allowed():
    # Commands work both in the configured control group and in the account's
    # private chat. This fixes the confusing situation where commands were
    # silently ignored when testing from the bot/user chat.
    return filters.private | filters.chat(CONTROL_GROUP_ID)


def _help_text():
    return (
        "🎙️ **VC Fighter — Commands**\n\n"
        "🔗 `/connect -1001234567890` — connect/relay to target VC\n"
        "🔗 `/join -1001234567890` — same as /connect\n"
        "▶️ `/start -1001234567890` — same as /connect\n"
        "⛔ `/stop` — stop relay and leave VCs\n"
        "🚪 `/leave` — same as /stop\n"
        "🔊 `/volume 0-300` — set volume percentage\n"
        "📊 `/status` — show current relay status\n"
        "❓ `/help` — show this help\n\n"
        "Example: `/connect -1001234567890`"
    )


def register(app):
    global bridge
    bridge = VCBridge(app)
    state.volume = DEFAULT_VOLUME
    allowed = _allowed()

    @app.on_message(filters.command("help") & allowed)
    async def help_cmd(_, message):
        await message.reply_text(_help_text())

    @app.on_message(filters.command("ping") & allowed)
    async def ping(_, message):
        await message.reply_text("🏓 Pong — VC Fighter is online.")

    @app.on_message(filters.command(["connect", "join", "start"]) & allowed)
    async def connect(_, message):
        if len(message.command) < 2:
            if message.command[0].lower() == "start":
                return await message.reply_text(_help_text())
            return await message.reply_text(
                "Usage: `/connect <target_group_id>`\n"
                "Example: `/connect -1001234567890`"
            )
        try:
            target = int(message.command[1])
        except ValueError:
            return await message.reply_text("❌ Target group ID must be a number.")

        await message.reply_text("⏳ Connecting to voice chats…")
        try:
            await bridge.start(message.chat.id, target)
            await message.reply_text(
                f"✅ **Relay connected**\nControl: `{message.chat.id}`\nTarget: `{target}`"
            )
        except Exception as exc:
            log.exception("Unable to connect relay")
            await message.reply_text(
                f"❌ **Relay start failed**\n`{type(exc).__name__}: {exc}`"
            )

    @app.on_message(filters.command("volume") & allowed)
    async def volume(_, message):
        if len(message.command) < 2:
            return await message.reply_text(
                f"🔊 Current volume: `{round(state.volume * 100)}%`\n"
                "Usage: `/volume <0-300>`"
            )
        try:
            percent = int(message.command[1])
        except ValueError:
            return await message.reply_text("❌ Volume must be a number from 0 to 300.")
        if not 0 <= percent <= 300:
            return await message.reply_text("❌ Volume must be between 0 and 300.")
        state.volume = percent / 100.0
        await message.reply_text(f"🔊 Volume set to **{percent}%**")

    @app.on_message(filters.command("status") & allowed)
    async def status(_, message):
        running = bool(bridge and bridge.running)
        control = state.control_chat_id
        target = state.target_chat_id
        await message.reply_text(
            "📊 **VC Fighter Status**\n\n"
            f"Relay: {'🟢 Running' if running else '🔴 Stopped'}\n"
            f"Control chat: `{control}`\n"
            f"Target chat: `{target}`\n"
            f"Volume: `{round(state.volume * 100)}%`"
        )

    @app.on_message(filters.command(["stop", "leave"]) & allowed)
    async def stop(_, message):
        try:
            await bridge.stop()
            await message.reply_text("⛔ Relay stopped. VC connections closed.")
        except Exception as exc:
            log.exception("Unable to stop relay")
            await message.reply_text(f"❌ Stop failed: `{type(exc).__name__}: {exc}`")
