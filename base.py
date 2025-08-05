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
Банкротство физических лиц – шанс начать жизнь с чистого листа?

🔹 Устали от бесконечных звонков коллекторов?
🔹 Каждый месяц – как замкнутый круг: зарплата уходит на долги?
🔹 Страшно открывать почту, брать трубку, боитесь, что описали имущество?

Стоп! Больше не нужно жить в стрессе и бесконечно гасить долги. Законное банкротство – это ваш выход!

Почему банкротство – это спасение?
✅ Спишем до 100% долгов – даже по кредитам, займам и штрафам.
✅ Остановим звонки коллекторов, суды и приставы – законная защита.
✅ Сохраним единственное жилье и необходимые вещи – их не заберут.
✅ Новый финансовый старт – без долгового бремени.

Как это работает?
1️⃣ Консультация – оценим вашу ситуацию.
2️⃣ Подготовка документов – сделаем всё за вас.
3️⃣ Сопровождение в суде – добьемся списания долгов.
Ваша же задача простая – кредиты не брать новые, текущие не платить, имущество не покупать/продавать. 

Мы поможем – без пустых обещаний
Мы не просто «оформляем банкротство» – мы возвращаем вам жизнь.

Не ждите, пока долги погубят ваше будущее!
Регистрируйтесь прямо сейчас – и через полгода сможете вздохнуть свободно.

Это ваш шанс на новую жизнь. Воспользуйтесь им!""", reply_markup=keyboard)

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