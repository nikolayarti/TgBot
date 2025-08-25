import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import (
    InlineKeyboardButton, InlineKeyboardMarkup,
    ReplyKeyboardMarkup, KeyboardButton
)
from aiogram.filters import CommandStart
from config import *

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
user_data = {}

# 🚀 Стартовая команда
@dp.message(CommandStart())
async def start(message: types.Message):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📝 Зарегистрироваться", callback_data="register")]
        ]
    )
    await message.answer("""
Замучили долги? Верните себе финансовую свободу с профессионалами с 13-летним опытом!

Компания «Старт» с 2012 года помогает людям легально списывать долги через банкротство. Наш высокий рейтинг в Яндексе и более 10 000 успешных дел — это ваша гарантия результата и спокойствия.

Почему выбирают нас?
✅ Эксперты с 2015 года: Мы работаем с момента вступления в силу закона о банкротстве физлиц и знаем все нюансы.
✅ Спишем до 100% долгов по кредитам, займам и штрафам — законно и безопасно.
✅ Полное сопровождение «под ключ»: От консультации до защиты в суде — все заботы на нас.
✅ Сохраним ваше имущество: Единственное жилье и необходимые вещи останутся с вами (согласно ст. 446 ГПК РФ).
✅ Ваша уверенность: Прописываем в договоре пожизненную гарантию защиты вас и вашего имущества5.

Как мы работаем?

Бесплатная консультация: Оценим вашу ситуацию и шансы на списание.

Подготовка документов: Соберем и оформим все за вас.

Сопровождение в суде: Наши юристы возьмут на себя общение с приставами и кредиторами.
Ваша задача — просто следовать нашим инструкциям.

Хватит жить в стрессе!
Доверьте решение проблемы лидерам с безупречной репутацией. Более 10 000 довольных клиентов и 100% выигранных дел говорят сами за себя.

Сделайте первый шаг к жизни без долгов — получите бесплатную консультацию прямо сейчас!
Через несколько месяцев вы сможете забыть о долгах навсегда.""", reply_markup=keyboard)

# 📱 Запрос номера телефона
@dp.callback_query(lambda c: c.data == "register")
async def ask_phone(callback: types.CallbackQuery):
    phone_keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="📱 Отправить номер", request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    await callback.message.answer("Пожалуйста, отправьте ваш номер телефона:", reply_markup=phone_keyboard)
    await callback.answer()

# ✅ Получение номера и запрос согласия
@dp.callback_query(lambda c: c.data == "register")
async def ask_phone(callback: types.CallbackQuery):
    phone_keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📱 Отправить номер", request_contact=True)],
            [KeyboardButton(text="✍️ Ввести вручную")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    await callback.message.answer(
        "Пожалуйста, отправьте ваш номер телефона.\nВы можете:\n• Нажать кнопку 📱 для автоматической отправки\n• Или ввести номер вручную в формате +79991234567",
        reply_markup=phone_keyboard
    )
    await callback.answer()

@dp.message(lambda m: m.contact or m.text)
async def handle_phone(message: types.Message):
    user = message.from_user
    phone = None

    if message.contact:
        phone = message.contact.phone_number
    elif message.text:
        text = message.text.strip()
        if text.startswith("+") and text[1:].isdigit() and 10 <= len(text) <= 15:
            phone = text
        else:
            await message.answer("❌ Неверный формат номера. Попробуйте снова, например: +79991234567")
            return

    user_data[str(user.id)] = {
        "name": f"{user.first_name or ''} {user.last_name or ''}".strip(),
        "username": f"@{user.username}" if user.username else "нет",
        "phone": phone
    }

    confirm_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Согласен на обработку данных", callback_data=f"consent_{user.id}")]
        ]
    )
    await message.answer("Спасибо! Подтвердите согласие на обработку персональных данных:", reply_markup=confirm_keyboard)

# 📩 Отправка заявки админу
@dp.callback_query(lambda c: c.data.startswith("consent_"))
async def send_application(callback: types.CallbackQuery):
    user_id = callback.data.split("_")[1]
    data = user_data.get(user_id)

    if not data:
        await callback.answer("Данные не найдены.")
        return

    text = (
        f"📥 Новая заявка:\n"
        f"👤 Имя: {data['name']}\n"
        f"📩 Username: {data['username']}\n"
        f"📞 Телефон: {data['phone']}\n"
        f"🆔 ID: {user_id}"
    )

    confirm_btn = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Подтвердить", callback_data=f"approve_{user_id}")]
        ]
    )

    await bot.send_message(chat_id=ADMIN_ID, text=text, reply_markup=confirm_btn)
    await callback.message.edit_text("✅ Заявка отправлена! Ожидайте подтверждение.")
    await callback.answer()

# 🎉 Подтверждение заявки
@dp.callback_query(lambda c: c.data.startswith("approve_"))
async def approve_user(callback: types.CallbackQuery):
    user_id = callback.data.split("_")[1]
    data = user_data.get(user_id)

    if not data:
        await callback.answer("Пользователь не найден.")
        return

    await bot.send_message(chat_id=int(user_id), text=f"""
🎉 {data['name']}, ваша регистрация подтверждена!

Перед началом процедуры банкротства важно правильно заполнить анкету, чтобы юрист мог оценить вашу ситуацию и предложить оптимальное решение:👉 
https://docs.google.com/forms/d/e/1FAIpQLSegf5gGuKxdegNJs8_49PusHtrSrtzP88-7ed2CHipR3W_jXw/viewform?usp=sharing
""")
    await callback.answer("Заявка подтверждена.")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())