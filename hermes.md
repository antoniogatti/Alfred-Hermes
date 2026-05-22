# Hermes Setup Notes

## Project Status
- Hermes installer completed successfully on May 21, 2026.
- Install command used:
  - `curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash`

## Credentials Files
Use these files as the source of truth for secrets:
- `AZURE_CREDENTIALS.env`
- `TELEGRAM_CREDENTIALS.env`
- `OPENROUTER_CREDENTIALS.env`

Do not duplicate real tokens in markdown files.

## Current Configuration Snapshot
### Telegram
- Bot username: `Ant_Alfref_bot`
- Bot name: `Ant_Alfref_bot`
- Bot token: saved in `TELEGRAM_CREDENTIALS.env` as `TELEGRAM_BOT_TOKEN`

### OpenRouter
- API key is saved in `OPENROUTER_CREDENTIALS.env` as `OPENROUTER_API_KEY`

### Azure
- Subscription name: `Ant Enterprise`
- Resource group: `OpenClaw`
- Location: `italynorth`
- VM: `openclaw-vm`
- Full Azure values are stored in `AZURE_CREDENTIALS.env`

## Telegram Configuration Documentation

### 1. Create Telegram Bot via BotFather
1. Open Telegram and chat with BotFather.
2. Run `/newbot`.
3. Set bot display name.
4. Set bot username ending with `bot`.
5. Copy the generated HTTP API token.

### 2. Save Telegram Credentials in Env File
Open `TELEGRAM_CREDENTIALS.env` and set:
- `TELEGRAM_BOT_TOKEN=<your token from BotFather>`
- `TELEGRAM_BOT_USERNAME=<your bot username>`
- `TELEGRAM_BOT_NAME=<your bot display name>`

Optional values:
- `TELEGRAM_API_ID` and `TELEGRAM_API_HASH` (only if your workflow needs MTProto/user client)
- `TELEGRAM_WEBHOOK_URL`
- `TELEGRAM_WEBHOOK_SECRET`
- `TELEGRAM_DEFAULT_CHAT_ID`
- `TELEGRAM_DEFAULT_CHANNEL_ID`

### 3. Load Env in Shell
```bash
source TELEGRAM_CREDENTIALS.env
```

### 4. Optional: Verify Token Works
```bash
curl "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/getMe"
```
A successful response should return `"ok": true`.

### 5. Optional: Find Chat ID
1. Send a message to your bot from Telegram.
2. Run:
```bash
curl "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/getUpdates"
```
3. Copy `message.chat.id` and save it in `TELEGRAM_DEFAULT_CHAT_ID`.

### 6. Security Best Practices
- Never commit credential env files.
- Rotate bot token immediately if exposed.
- Restrict bot permissions to only what Hermes needs.
- Keep webhook secrets random and long if webhook mode is used.

## Home Assistant Note
If you do not run Home Assistant, leave the Home Assistant Long-Lived Access Token blank during Hermes setup.
Google Home mobile usage alone does not provide a Home Assistant token.
