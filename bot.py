import logging
from config import TOKEN
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from config import BOT_TOKEN, CHANNEL_USERNAME, ADMIN_USERNAME

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

user_lang = {}

texts = {
    "subscribe": {
        "uz": "Botdan foydalanish uchun kanalga obuna bo‘ling",
        "ru": "Чтобы пользоваться ботом, подпишитесь на канал",
        "en": "To use the bot, please subscribe to the channel"
    },
    "choose_subject": {
        "uz": "Fanni tanlang",
        "ru": "Выберите предмет",
        "en": "Choose a subject"
    },
    "contact": {
        "uz": "Admin bilan bog‘lanish",
        "ru": "Связаться с администратором",
        "en": "Contact admin"
    }
}

# ============ START ============
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    kb = types.InlineKeyboardMarkup()
    kb.add(
        types.InlineKeyboardButton("🇺🇿 O‘zbek", callback_data="lang_uz"),
        types.InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru"),
        types.InlineKeyboardButton("🇬🇧 English", callback_data="lang_en"),
    )

    await message.answer("Tilni tanlang / Choose language", reply_markup=kb)

# ============ LANGUAGE ============
@dp.callback_query_handler(lambda c: c.data.startswith("lang_"))
async def set_lang(call: types.CallbackQuery):
    lang = call.data.split("_")[1]
    user_lang[call.from_user.id] = lang

    kb = types.InlineKeyboardMarkup()
    kb.add(
        types.InlineKeyboardButton(
            "📢 Kanalga o‘tish",
            url=f"https://t.me/{CHANNEL_USERNAME}"
        )
    )
    kb.add(
        types.InlineKeyboardButton(
            "✅ Obuna bo‘ldim",
            callback_data="check_sub"
        )
    )

    await call.message.edit_text(texts["subscribe"][lang], reply_markup=kb)

# ============ SUB CHECK ============
@dp.callback_query_handler(lambda c: c.data == "check_sub")
async def check_sub(call: types.CallbackQuery):
    lang = user_lang.get(call.from_user.id, "uz")

    try:
        member = await bot.get_chat_member(
            f"@{CHANNEL_USERNAME}",
            call.from_user.id
        )
        if member.status not in ["member", "administrator", "creator"]:
            await call.answer("Avval kanalga obuna bo‘ling!", show_alert=True)
            return
    except:
        await call.answer("Avval kanalga obuna bo‘ling!", show_alert=True)
        return

    kb = types.InlineKeyboardMarkup()
    kb.add(
        types.InlineKeyboardButton("📘 Arab tili fonetika", callback_data="fonetika"),
        types.InlineKeyboardButton("📙 Arab tili grammatika", callback_data="grammatika")
    )

    await call.message.edit_text(texts["choose_subject"][lang], reply_markup=kb)

# ============ SUBJECT ============
@dp.callback_query_handler(lambda c: c.data in ["fonetika", "grammatika"])
async def subject(call: types.CallbackQuery):
    lang = user_lang.get(call.from_user.id, "uz")

    kb = types.InlineKeyboardMarkup()
    kb.add(
        types.InlineKeyboardButton(
            texts["contact"][lang],
            url=f"https://t.me/{ADMIN_USERNAME}"
        )
    )

    await call.message.edit_text("👇", reply_markup=kb)

# ============ RUN ============
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
