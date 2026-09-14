# VC Fighter — Railway Fixed v3

Telegram voice-chat relay: audio from the configured control VC is forwarded
into a target VC with adjustable volume.

## Why v3 fixes the Railway build error

The old project pinned `pytgcalls==2.1.0`, whose dependency chain requires the
old `tgcalls==2.0.0` package. That old package does not provide a usable Linux
wheel for the Railway Python environment, which caused `No matching
 distribution found for tgcalls==2.0.0`.

This build uses the current `py-tgcalls` package and its NTgCalls backend,
which provides prebuilt Linux wheels and supports modern Python versions.
Python is pinned to 3.11 with `.python-version` for a predictable Railway
build.

## Railway variables

Set these in Railway → Service → Variables:

- `API_ID` — Telegram API ID
- `API_HASH` — Telegram API hash
- `CONTROL_GROUP_ID` — group where commands are accepted
- `SESSION_STRING` — optional Pyrogram StringSession. Recommended for a
  non-interactive Railway deployment.
- `SESSION_NAME` — optional, defaults to `relay` when using a file session
- `DEFAULT_VOLUME` — optional, defaults to `1.0`

Do not commit real API credentials or a session string to GitHub.

## Commands

Send these in the configured control group:

- `/connect <target_group_id>`
- `/volume <0-300>`
- `/stop`

## Relay behavior

When `/connect` is used, the service joins the control VC and target VC. It
captures incoming PCM16 audio frames from the control VC, mixes multiple
incoming sources, applies the configured volume, and injects the result into
the target VC.

The old FFmpeg stdin/stdout relay was removed because the old implementation
never actually fed Telegram VC audio into that pipe.
