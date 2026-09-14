# VCFighter Railway Relay

Telegram Voice Chat relay using Pyrogram and PyTgCalls.

## Railway variables
Set:
- `API_ID`
- `API_HASH`
- `SESSION_STRING`
- `CONTROL_GROUP_ID`
- `DEFAULT_VOLUME` (optional, default `1.0`)

## Commands
Commands now respond in both the configured control group and the private chat:

- `/help`
- `/ping`
- `/connect <target_group_id>`
- `/join <target_group_id>`
- `/start <target_group_id>`
- `/stop`
- `/leave`
- `/volume <0-300>`
- `/status`

Example:
`/connect -1001234567890`

Do not commit Telegram credentials or session strings to GitHub.
