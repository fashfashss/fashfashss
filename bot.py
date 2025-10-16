import os
import asyncio
import sqlite3
from aiogram import Bot, Dispatcher, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

# ====== Конфигурация ======
TOKEN = os.getenv("TOKEN")
ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID"))
# ==========================

bot = Bot(
    token=TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()

# ====== SQLite база ======
conn = sqlite3.connect("messages.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    message_type TEXT,
    content TEXT,
    file_id TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    forwarded INTEGER DEFAULT 0
)
""")
conn.commit()

# ====== Функции для работы с БД ======
def save_message(user_id, message_type, content=None, file_id=None):
    cursor.execute("""
        INSERT INTO messages (user_id, message_type, content, file_id)
        VALUES (?, ?, ?, ?)
    """, (user_id, message_type, content, file_id))
    conn.commit()

def get_unforwarded():
    cursor.execute("SELECT * FROM messages WHERE forwarded = 0 ORDER BY id")
    return cursor.fetchall()

def mark_forwarded(msg_id):
    cursor.execute("UPDATE messages SET forwarded = 1 WHERE id = ?", (msg_id,))
    conn.commit()

# ====== Пересылка накопленных сообщений ======
async def forward_unforwarded_messages():
    messages = get_unforwarded()
    for msg in messages:
        msg_id, user_id, msg_type, content, file_id, timestamp, forwarded = msg
        try:
            if msg_type == "text":
                await bot.send_message(ADMIN_CHAT_ID, f"[{timestamp}] {content}")
            elif msg_type == "photo":
                await bot.send_photo(ADMIN_CHAT_ID, file_id, caption=content or "")
            elif msg_type == "video":
                await bot.send_video(ADMIN_CHAT_ID, file_id, caption=content or "")
            elif msg_type == "voice":
                await bot.send_voice(ADMIN_CHAT_ID, file_id, caption=content or "")
            elif msg_type == "document":
                await bot.send_document(ADMIN_CHAT_ID, file_id, caption=content or "")
            elif msg_type == "sticker":
                await bot.send_sticker(ADMIN_CHAT_ID, file_id)
        except Exception as e:
            print(f"Ошибка при пересылке накопленного сообщения: {e}")
        mark_forwarded(msg_id)

# ====== Основной хэндлер сообщений ======
@dp.message()
async def handle_message(message: types.Message):
    user_id = message.chat.id

    # Определяем тип сообщения
    msg_type = "text"
    content = message.text
    file_id = None

    if message.photo:
        msg_type = "photo"
        file_id = message.photo[-1].file_id
        content = message.caption or ""
    elif message.video:
        msg_type = "video"
        file_id = message.video.file_id
        content = message.caption or ""
    elif message.voice:
        msg_type = "voice"
        file_id = message.voice.file_id
        content = message.caption or ""
    elif message.document:
        msg_type = "document"
        file_id = message.document.file_id
        content = message.caption or ""
    elif message.sticker:
        msg_type = "sticker"
        file_id = message.sticker.file_id
        content = None

    # Сохраняем в базу
    save_message(user_id, msg_type, content, file_id)

    # Если пишет не админ — пересылаем админу сразу
    if user_id != ADMIN_CHAT_ID:
        await forward_unforwarded_messages()

    # Если пишет админ — проверяем reply
    else:
        if not message.reply_to_message:
            await bot.send_message(
                ADMIN_CHAT_ID,
                "⚠️ Чтобы ответить пользователю, сделайте reply на пересланное сообщение."
            )
            return

        # Находим пользователя, которому отправляем
        replied_id = message.reply_to_message.message_id
        cursor.execute("SELECT user_id FROM messages WHERE id = ?", (replied_id,))
        row = cursor.fetchone()
        if not row:
            await bot.send_message(ADMIN_CHAT_ID, "⚠️ Не удалось определить пользователя для ответа.")
            return
        target_user_id = row[0]

        # Пересылаем ответ в зависимости от типа
        if message.text:
            await bot.send_message(target_user_id, message.text)
        elif message.photo:
            await bot.send_photo(target_user_id, message.photo[-1].file_id, caption=message.caption or "")
        elif message.video:
            await bot.send_video(target_user_id, message.video.file_id, caption=message.caption or "")
        elif message.voice:
            await bot.send_voice(target_user_id, message.voice.file_id, caption=message.caption or "")
        elif message.document:
            await bot.send_document(target_user_id, message.document.file_id, caption=message.caption or "")
        elif message.sticker:
            await bot.send_sticker(target_user_id, message.sticker.file_id)

# ====== Запуск бота ======
async def main():
    print("🤖 Бот запущен и слушает сообщения...")
    # При старте пересылаем все накопленные сообщения
    await forward_unforwarded_messages()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
