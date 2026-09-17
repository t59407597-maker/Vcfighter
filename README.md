# VCFighter — Railway VC Player

## Features
- `/allvc join` scans the session account's joined groups and attempts to join every active Voice Chat; no group IDs are required.
- `/allvc leave` leaves all VCs joined by the session.
- `/join <group_id>` joins one specific VC.
- Reply to an audio/voice message and use `/fight` to repeat the recorded audio in the selected VC.
- `/fightstop` stops playback while keeping the account in the VC.
- Automatic group reactions: first-seen users are scheduled for 30 minutes; users already seen in the running process are scheduled for 1 hour.

## Railway variables
- `API_ID`
- `API_HASH`
- `SESSION_STRING`
- `NEW_USER_REACTION_DELAY=1800`
- `OLD_USER_REACTION_DELAY=3600`

The app uses a Pyrogram user session, not a BotFather bot token.

## Commands
- `/allvc join`
- `/allvc leave`
- `/join <group_id>`
- `/fight` — reply to audio/voice
- `/fightstop`
- `/status`
- `/leave [group_id]`
- `/reaction on`
- `/reaction off`
- `/name Rexxxxxxxxy` — normalizes repeated letters to `rexy` for safe audio labels.

Fight playback uses the exact recorded audio supplied by the user; it does not synthesize or generate new spoken content.


V6 compatibility: PyTgCalls `.app` compatibility alias and active-VC-only join/play behavior.

## Single-VC fight flow (v12)

- `/join <group_id>` selects and joins that group's active voice chat.
- Reply to an audio/voice message with `/fight` in the same group. The recorded audio is played repeatedly in the selected VC.
- `/fightstop` stops the fight audio while keeping the account connected to the VC.
- `/leave` and `/allvc leave` keep their existing behavior.
