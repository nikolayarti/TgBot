from aiogram import Bot, Dispatcher, types
from aiogram.types import (
    InlineKeyboardButton, InlineKeyboardMarkup
)
from aiogram.filters import CommandStart
import asyncio
from config import *



bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
user_applications = {}

@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📝 Зарегистрироваться", callback_data="register")]
        ]
    )
    await message.answer(
"""
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

Это ваш шанс на новую жизнь. Воспользуйтесь им!""",
        reply_markup=keyboard
    )

@dp.callback_query(lambda c: c.data == "register")
async def handle_registration(callback: types.CallbackQuery):
    user = callback.from_user
    full_name = f"{user.first_name or ''} {user.last_name or ''}".strip()
    username = f"@{user.username}" if user.username else "нет"

    user_applications[str(user.id)] = full_name

    application_text = (
        f"Новая заявка!\n"
        f"👤 Имя: {full_name}\n"
        f"🆔 ID: {user.id}\n"
        f"📩 Username: {username}"
    )

    confirm_btn = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Подтвердить", callback_data=f"confirm_{user.id}")]
        ]
    )

    await bot.send_message(chat_id=ADMIN_ID, text=application_text, reply_markup=confirm_btn)
    await callback.message.edit_text("✅ Заявка отправлена! Ожидайте подтверждение.")
    await callback.answer()

@dp.callback_query(lambda c: c.data.startswith("confirm_"))
async def confirm_application(callback: types.CallbackQuery):
    user_id = int(callback.data.split("_")[1])
    name = user_applications.get(str(user_id), "Пользователь")

    await bot.send_message(chat_id=user_id, text=f"""
🎉 {name}, ваша регистрация подтверждена!
Перед началом процедуры банкротства важно правильно заполнить анкету, чтобы юрист мог оценить вашу ситуацию и предложить оптимальное решение.
https://docs.google.com/forms/d/e/1FAIpQLSegf5gGuKxdegNJs8_49PusHtrSrtzP88-7ed2CHipR3W_jXw/viewform?usp=sharing&ouid=109953191210317206978""")
    await callback.answer("Вы подтвердили заявку.")


async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())