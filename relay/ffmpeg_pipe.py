"""Compatibility module kept for older project imports.

The relay no longer needs an FFmpeg stdin/stdout pipe. PyTgCalls delivers
PCM16 audio frames directly, so doing volume processing in Python avoids the
broken RawAudioStream/tgcalls 2.0 dependency path.
"""

from array import array

from relay import state


def apply_volume(pcm16: bytes) -> bytes:
    """Scale signed 16-bit little-endian PCM without changing its format."""
    volume = float(state.volume)
    if volume == 1.0:
        return pcm16

    samples = array("h")
    samples.frombytes(pcm16)

    if samples.itemsize != 2:
        return pcm16

    for i, sample in enumerate(samples):
        value = int(sample * volume)
        if value > 32767:
            value = 32767
        elif value < -32768:
            value = -32768
        samples[i] = value

    return samples.tobytes()


def start_ffmpeg():
    """Deprecated compatibility stub; FFmpeg is no longer used by the relay."""
    raise RuntimeError("FFmpeg pipe is no longer used; PyTgCalls handles PCM frames directly.")
