import asyncio
import logging
import os
import subprocess

from pytgcalls import PyTgCalls

from relay import state

log = logging.getLogger(__name__)


class VCBridge:
    """Join one Telegram voice chat and continuously play the selected audio."""

    def __init__(self, app):
        self.calls = PyTgCalls(app)
        self.running = False
        self._started = False
        self._fight_task = None
        self._lock = asyncio.Lock()

    async def _ensure_started(self):
        if not self._started:
            await self.calls.start()
            self._started = True

    @staticmethod
    async def _duration(path: str) -> float:
        """Get media duration using ffprobe; fall back safely if unavailable."""
        try:
            proc = await asyncio.create_subprocess_exec(
                "ffprobe", "-v", "error", "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1", path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.DEVNULL,
            )
            out, _ = await proc.communicate()
            value = float(out.decode().strip())
            if value > 0:
                return value
        except Exception:
            log.exception("Unable to detect audio duration")
        return 30.0

    async def join(self, chat_id: int):
        async with self._lock:
            await self._ensure_started()
            if state.target_chat_id and state.target_chat_id != chat_id:
                try:
                    await self.calls.leave_call(state.target_chat_id)
                except Exception:
                    log.exception("Failed to leave previous VC %s", state.target_chat_id)
            state.target_chat_id = chat_id
            self.running = True
            # A tiny silent/empty stream is not required here. play() below will
            # join the existing voice chat when /fight is used.
            return chat_id

    async def fight(self, path: str):
        async with self._lock:
            if not state.target_chat_id:
                raise RuntimeError("No voice chat joined. Use /join <group_id> first.")
            if not os.path.exists(path):
                raise FileNotFoundError(path)

            await self._ensure_started()
            await self._cancel_fight_unlocked()

            state.fight_file = path
            state.fight_running = True
            target = state.target_chat_id
            self._fight_task = asyncio.create_task(self._fight_loop(target, path))

    async def _fight_loop(self, target: int, path: str):
        try:
            while state.fight_running and state.target_chat_id == target:
                if not os.path.exists(path):
                    raise FileNotFoundError(path)
                duration = await self._duration(path)
                # play() joins/streams the file into the VC. Re-playing after the
                # measured duration gives us a simple reliable loop without
                # depending on version-specific stream-end callback names.
                await self.calls.play(target, path)
                await asyncio.sleep(max(1.0, duration - 0.25))
        except asyncio.CancelledError:
            raise
        except Exception:
            log.exception("Fight playback failed")
            state.fight_running = False
        finally:
            if not state.fight_running:
                try:
                    if os.path.exists(path):
                        os.remove(path)
                except OSError:
                    pass

    async def _cancel_fight_unlocked(self):
        state.fight_running = False
        task = self._fight_task
        self._fight_task = None
        if task and not task.done():
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass

    async def stop_fight(self):
        async with self._lock:
            await self._cancel_fight_unlocked()
            state.fight_file = None

    async def leave(self):
        async with self._lock:
            await self._cancel_fight_unlocked()
            target = state.target_chat_id
            state.target_chat_id = None
            state.fight_file = None
            self.running = False
            if target is not None:
                try:
                    await self.calls.leave_call(target)
                except Exception:
                    log.exception("Failed to leave VC %s", target)

    async def status(self):
        return {
            "target": state.target_chat_id,
            "joined": bool(state.target_chat_id),
            "fight": bool(state.fight_running),
            "file": state.fight_file,
        }
