import asyncio
import logging

from pytgcalls import PyTgCalls
from pytgcalls import filters as call_filters
from pytgcalls.types import Device, Direction, ExternalMedia, MediaStream, RecordStream, StreamFrames
from pytgcalls.types.raw import AudioParameters

from relay import state
from relay.ffmpeg_pipe import apply_volume


log = logging.getLogger(__name__)

AUDIO = AudioParameters(bitrate=48000, channels=2)


class VCBridge:
    """Relay incoming audio from one Telegram VC into another VC."""

    def __init__(self, app):
        self.calls = PyTgCalls(app)
        self.running = False
        self._lock = asyncio.Lock()

        @self.calls.on_update(
            call_filters.stream_frame(
                Direction.INCOMING,
                Device.MICROPHONE,
            )
        )
        async def on_audio(_, update: StreamFrames):
            if not self.running or state.target_chat_id is None:
                return

            # A StreamFrames update can contain frames from multiple incoming
            # sources. Mix them so everyone in the target VC hears the control VC.
            if not update.frames:
                return

            frame_len = max(len(frame.frame) for frame in update.frames)
            mixed = [0] * (frame_len // 2)

            for frame in update.frames:
                raw = frame.frame
                for i in range(0, len(raw) - 1, 2):
                    sample = int.from_bytes(raw[i:i + 2], "little", signed=True)
                    mixed[i // 2] += sample

            count = len(update.frames)
            out = bytearray(frame_len)
            for i, value in enumerate(mixed):
                value //= count
                if value > 32767:
                    value = 32767
                elif value < -32768:
                    value = -32768
                out[2 * i:2 * i + 2] = int(value).to_bytes(
                    2, "little", signed=True
                )

            await self.calls.send_frame(
                state.target_chat_id,
                Device.MICROPHONE,
                apply_volume(bytes(out)),
            )

    async def start(self, control_chat_id: int, target_chat_id: int):
        async with self._lock:
            if self.running:
                await self.stop()

            state.control_chat_id = control_chat_id
            state.target_chat_id = target_chat_id

            self.calls.start()

            # Join the control VC and capture incoming audio.
            await self.calls.play(
                control_chat_id,
                MediaStream(
                    ExternalMedia.AUDIO,
                    AUDIO,
                ),
            )
            await self.calls.record(
                control_chat_id,
                RecordStream(
                    audio=True,
                    audio_parameters=AUDIO,
                ),
            )

            # Join the target VC with an external audio source. Incoming
            # frames from the control VC are injected with send_frame().
            await self.calls.play(
                target_chat_id,
                MediaStream(
                    ExternalMedia.AUDIO,
                    AUDIO,
                ),
            )

            self.running = True
            log.info("Relay connected: %s -> %s", control_chat_id, target_chat_id)

    async def stop(self):
        async with self._lock:
            self.running = False

            for chat_id in (state.control_chat_id, state.target_chat_id):
                if chat_id is None:
                    continue
                try:
                    await self.calls.leave_call(chat_id)
                except Exception:
                    log.exception("Failed to leave call %s", chat_id)

            state.control_chat_id = None
            state.target_chat_id = None
