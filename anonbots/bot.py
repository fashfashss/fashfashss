import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

# === НАСТРОЙКА ===
TOKEN = "ТВОЙ_ТОКЕН_БОТА"   # Вставь сюда токен от BotFather
ADMIN_CHAT_ID = 123456789    # Вставь сюда свой chat_id (НЕ username!)
# =================

bot = Bot(
    token=TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()

# Словарь для хранения соответствий: пересланное сообщение → id пользователя
user_map = {}


@dp.message()
async def handle_message(message: types.Message):
    """Основная логика пересылки между пользователями и админом"""
    try:
        # Если пишет пользователь, пересылаем админу
        if message.chat.id != ADMIN_CHAT_ID:
            fwd = await message.forward(ADMIN_CHAT_ID)
            user_map[fwd.message_id] = message.chat.id

        # Если пишет админ — проверяем, ответил ли он на пересланное сообщение
        else:
            if not message.reply_to_message:
                await bot.send_message(
                    ADMIN_CHAT_ID,
                    "⚠️ Чтобы ответить пользователю, сделай <b>ответ (Reply)</b> на пересланное сообщение."
                )
                return

            # Находим, кому нужно переслать ответ
            user_id = user_map.get(message.reply_to_message.message_id)
            if not user_id:
                await bot.send_message(
                    ADMIN_CHAT_ID,
                    "⚠️ Не удалось определить, кому отправить сообщение (нет связи с исходным)."
                )
                return

            # Пересылаем ответ пользователю (любого типа)
            if message.text:
                await bot.send_message(user_id, message.text)
            elif message.photo:
                await bot.send_photo(user_id, message.photo[-1].file_id, caption=message.caption or "")
            elif message.video:
                await bot.send_video(user_id, message.video.file_id, caption=message.caption or "")
            elif message.voice:
                await bot.send_voice(user_id, message.voice.file_id, caption=message.caption or "")
            elif message.document:
                await bot.send_document(user_id, message.document.file_id, caption=message.caption or "")
            elif message.sticker:
                await bot.send_sticker(user_id, message.sticker.file_id)
            else:
                await bot.send_message(user_id, "⚠️ Тип сообщения пока не поддерживается.")
    except Exception as e:
        print(f"Ошибка: {e}")


async def main():
    print("🤖 Бот запущен и слушает сообщения...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())


