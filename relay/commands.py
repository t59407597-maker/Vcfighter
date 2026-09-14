import logging
import os
import uuid

from pyrogram import filters
from pyrogram.types import Message

from config import CONTROL_GROUP_ID
from relay import state
from relay.vc_bridge import VCBridge

log = logging.getLogger(__name__)
bridge = None
DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)


def _allowed():
    return filters.private | filters.chat(CONTROL_GROUP_ID)


def _help_text():
    return (
        "🎙️ **VC Fighter**\n\n"
        "1️⃣ `/join -1001234567890` — target group VC join\n"
        "2️⃣ VC me join hone ke baad, kisi **audio/voice** ko reply karke `/fight` bhejo\n"
        "3️⃣ `/fight` — replied audio ko VC me continuously play karega\n"
        "4️⃣ `/fightstop` — audio playback stop, VC me bana rahega\n"
        "5️⃣ `/leave` — VC leave\n"
        "6️⃣ `/status` — current status\n"
        "7️⃣ `/ping` — bot online check\n"
        "8️⃣ `/help` — commands\n\n"
        "Example:\n"
        "`/join -1001234567890`\n"
        "phir audio par reply → `/fight`"
    )


def _is_audio(msg: Message) -> bool:
    return bool(msg and (msg.audio or msg.voice))


def register(app):
    global bridge
    bridge = VCBridge(app)
    allowed = _allowed()

    @app.on_message(
        (filters.command(["help", "commands", "menu", "h"]) |
         filters.regex(r"^/(?:help|commands|menu|h)(?:@[A-Za-z0-9_]+)?(?:\s|$)")) & allowed
    )
    async def help_cmd(_, message):
        await message.reply_text(_help_text())

    @app.on_message(filters.command("ping") & allowed)
    async def ping(_, message):
        await message.reply_text("🏓 Pong — VC Fighter is online.")

    @app.on_message(filters.command("join") & allowed)
    async def join_cmd(_, message):
        if len(message.command) < 2:
            return await message.reply_text(
                "Usage: `/join <group_id>`\nExample: `/join -1001234567890`"
            )
        try:
            target = int(message.command[1])
        except ValueError:
            return await message.reply_text("❌ Group ID must be a number.")

        status = await message.reply_text("⏳ VC join kar raha hoon…")
        try:
            await bridge.join(target)
            await status.edit_text(
                f"✅ **VC joined/ready**\nGroup: `{target}`\n\n"
                "Ab kisi audio/voice ko reply karke `/fight` bhejo."
            )
        except Exception as exc:
            log.exception("VC join failed")
            await status.edit_text(
                f"❌ **VC join failed**\n`{type(exc).__name__}: {exc}`\n\n"
                "Check karo: group me active Voice Chat hona chahiye aur account ko join/speak permission honi chahiye."
            )

    @app.on_message(filters.command("fight") & allowed)
    async def fight_cmd(_, message):
        if not state.target_chat_id:
            return await message.reply_text("❌ Pehle `/join <group_id>` karo.")

        replied = message.reply_to_message
        if not _is_audio(replied):
            return await message.reply_text(
                "❌ `/fight` ko **audio/voice message ke reply** me bhejo."
            )

        status = await message.reply_text("⬇️ Audio download ho raha hai…")
        path = None
        try:
            ext = ".ogg" if replied.voice else ".mp3"
            path = os.path.join(DOWNLOAD_DIR, f"fight_{uuid.uuid4().hex}{ext}")
            await replied.download(file_name=path)
            await bridge.fight(path)
            await status.edit_text(
                f"🔥 **FIGHT started**\nVC: `{state.target_chat_id}`\n\n"
                "Audio repeat me play hota rahega.\n`/fightstop` se stop karo."
            )
        except Exception as exc:
            if path and os.path.exists(path):
                try:
                    os.remove(path)
                except OSError:
                    pass
            log.exception("Fight playback failed")
            await status.edit_text(
                f"❌ **Fight failed**\n`{type(exc).__name__}: {exc}`"
            )

    @app.on_message(filters.command("fightstop") & allowed)
    async def fightstop_cmd(_, message):
        try:
            await bridge.stop_fight()
            await message.reply_text("🛑 Fight audio stopped. VC me bot bana hua hai.")
        except Exception as exc:
            log.exception("Fight stop failed")
            await message.reply_text(f"❌ Stop failed: `{type(exc).__name__}: {exc}`")

    @app.on_message(filters.command(["leave", "stop"]) & allowed)
    async def leave_cmd(_, message):
        try:
            await bridge.leave()
            await message.reply_text("🚪 VC left. Fight audio stopped.")
        except Exception as exc:
            log.exception("VC leave failed")
            await message.reply_text(f"❌ Leave failed: `{type(exc).__name__}: {exc}`")

    @app.on_message(filters.command("status") & allowed)
    async def status_cmd(_, message):
        s = await bridge.status()
        await message.reply_text(
            "📊 **VC Fighter Status**\n\n"
            f"VC: `{s['target']}`\n"
            f"Joined: {'🟢 Yes' if s['joined'] else '🔴 No'}\n"
            f"Fight: {'🟢 Playing' if s['fight'] else '🔴 Stopped'}"
        )
