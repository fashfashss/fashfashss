# Telegram Anonymous Bot

## Overview
This is a Telegram bot that enables anonymous communication between users and an admin. Users can send messages to the bot, which forwards them to an admin. The admin can reply to users through the bot, maintaining user anonymity.

**Current State:** Running and operational

## Recent Changes
- **October 16, 2025**: Initial project setup in Replit environment
  - Moved bot files from `anonbots/` to root directory
  - Configured environment secrets (TOKEN, ADMIN_CHAT_ID)
  - Installed Python 3.11 and aiogram library (v3.22.0)
  - Set up workflow to run the bot automatically
  - Created SQLite database for message storage

## Project Architecture

### Core Files
- `bot.py` - Main bot application with message handling logic
- `requirements.txt` - Python dependencies (aiogram>=3.7.1)
- `messages.db` - SQLite database storing messages and forwarding status

### Technology Stack
- **Language:** Python 3.11
- **Bot Framework:** aiogram 3.22.0
- **Database:** SQLite (local file-based)
- **Deployment:** Replit workflow (always running)

### Key Features
1. **Anonymous Messaging:** Users send messages to bot, forwarded to admin
2. **Admin Replies:** Admin can reply by replying to forwarded messages
3. **Multiple Media Types:** Supports text, photos, videos, voice, documents, and stickers
4. **Message Persistence:** All messages stored in SQLite database
5. **Automatic Forwarding:** Messages forwarded to admin in real-time

## Environment Configuration

### Required Secrets
- `TOKEN` - Telegram bot token from BotFather
- `ADMIN_CHAT_ID` - Telegram chat ID of the admin user

These are configured in Replit Secrets and automatically loaded as environment variables.

## How It Works

### Message Flow
1. User sends message to bot
2. Bot saves message to SQLite database
3. If sender is not admin, message is immediately forwarded to admin
4. Admin sees forwarded message with timestamp
5. Admin replies by using Telegram's reply feature
6. Bot identifies original sender and forwards admin's reply

### Database Schema
```sql
messages (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    message_type TEXT,
    content TEXT,
    file_id TEXT,
    timestamp DATETIME,
    forwarded INTEGER
)
```

## Running the Bot
The bot runs automatically via the "Telegram Bot" workflow. It executes `python bot.py` and displays console output.

Status indicator: "🤖 Бот запущен и слушает сообщения..." means the bot is running successfully.
