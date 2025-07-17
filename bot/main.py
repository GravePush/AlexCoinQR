import asyncio
from datetime import datetime, timedelta, timezone

import pytz
from aiogram import Bot, types, Dispatcher, F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import BufferedInputFile, Message
import qrcode
from io import BytesIO
from api.service import VisitorService
from bot.service import InviterService
from bot.utils import generate_ref_code
from config import BOT_API, CHAT_LINK, DOMAIN
from database import async_session_maker
from keyboards import *

bot = Bot(token=BOT_API)
dp = Dispatcher()
ADMIN_IDS = []

form_router = Router()


class QRForm(StatesGroup):
    telegram_id = State()
    username = State()


@dp.message(Command("start"))
async def handle_start(message: Message):
    args = message.text.split()
    ref_code = args[1] if len(args) > 1 else None
    telegram_id = message.from_user.id
    username = message.from_user.username

    if telegram_id in ADMIN_IDS:
        return await message.answer(
            "👨‍💼 Привет, админ!\n"
            "🔹 Здесь ты можешь создавать новые куар коды и просматривать статистику по ним.\n"
            "Для этого выбери команду:",
            reply_markup=main_admin_inline_keyboard
        )

    async with async_session_maker() as session:
        visitor = await VisitorService.get_one_or_none(
            session=session,
            telegram_id=telegram_id
        )

        if ref_code:
            inviter = await InviterService.get_one_or_none(session=session, ref_code=ref_code)

            if not inviter:
                return await message.answer("❌ Неверный QR-код. Попробуйте ещё раз.")

            if not visitor:
                await VisitorService.create(
                    session=session,
                    ref_code=ref_code,
                    username=username,
                    telegram_id=telegram_id,
                    inviter_id=inviter.id
                )

                inviter.click_count += 1
                await session.commit()
                return await message.answer(
                    f"✅ Добро пожаловать, @{username}!\n"
                    f"Подписывайтесь на чат: {CHAT_LINK}.\n\n"
                    f"Выберите команду:",
                    reply_markup=main_user_inline_keyboard
                )

        if visitor:
            return await message.answer(
                f"👋 С возвращением, @{username}!\n\n"
                f"Выберите команду:",
                reply_markup=main_user_inline_keyboard
            )

        return await message.answer(
            f"✅ Добро пожаловать, @{username}!\n"
            f"Подписывайтесь на чат: {CHAT_LINK}.\n\n"
            f"Выберите команду:",
            reply_markup=main_user_inline_keyboard
        )


@dp.callback_query(F.data == "newqr")
async def start_process_qr(callback: types.CallbackQuery, state: FSMContext):
    admin_telegram_id = callback.from_user.id
    if admin_telegram_id not in ADMIN_IDS:
        await callback.message.answer(
            "У вас нет доступа к этой команде!",
            reply_markup=back_to_main_inline_btn
        )
        return await callback.answer()
    await state.set_state(QRForm.telegram_id)
    await callback.message.answer("Введите Telegram ID пользователя (числом):")
    await callback.answer()


@dp.message(QRForm.telegram_id)
async def process_telegram_id(message: Message, state: FSMContext):
    if not message.text.isdigit():
        return await message.answer("❌ Введите числовой Telegram ID.")

    await state.update_data(telegram_id=int(message.text))
    await message.answer("Теперь введите username пользователя:")
    await state.set_state(QRForm.username)


@dp.message(QRForm.telegram_id)
async def process_telegram_id(message: Message, state: FSMContext):
    if not message.text.isdigit():
        return await message.answer("❌ Введите числовой Telegram ID.")

    await state.update_data(telegram_id=int(message.text))
    await state.set_state(QRForm.username)
    await message.answer("Теперь введите username:")


@dp.message(QRForm.username)
async def process_username_and_finish_fsm(message: Message, state: FSMContext):
    username = message.text.strip().lstrip("@")
    await state.update_data(username=username)

    data = await state.get_data()
    await state.clear()

    await generate_and_send_qr(
        message=message,
        telegram_id=data["telegram_id"],
        username=data["username"]
    )


async def generate_and_send_qr(
        message: Message,
        telegram_id: int,
        username: str,
        days: int = 30,
):
    async with async_session_maker() as session:
        existing_user = await InviterService.get_one_or_none(
            session=session,
            telegram_id=telegram_id
        )

    if existing_user:
        now = datetime.now(timezone.utc)

        expiry_datetime = existing_user.created_at + timedelta(days=days)

        if expiry_datetime > now:
            return await message.answer(
                f"ℹ️ У пользователя уже есть свой QR код, который действует до {expiry_datetime.strftime('%d.%m.%Y')}!",
                reply_markup=back_to_main_inline_btn
            )

    new_ref_code = generate_ref_code()
    async with async_session_maker() as session:
        await InviterService.create(
            session=session,
            telegram_id=telegram_id,
            ref_code=new_ref_code,
            username=username,
            click_count=0
        )

    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(f"{DOMAIN}{new_ref_code}")
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    buf = BytesIO()
    img.save(buf, format="PNG")
    qr_bytes = buf.getvalue()

    await message.reply_photo(
        photo=BufferedInputFile(qr_bytes, filename=f"qr_code_{username}.png"),
        caption=f"""
    🤖 QR-код для @{username}
    🎯 Реферальный код: {new_ref_code}
    🔗 Ссылка: {DOMAIN}{new_ref_code}
    ⏳ Срок действия: {days} дней
    📅 До: {(datetime.now() + timedelta(days=days)).strftime('%d.%m.%Y')}
    """
    )
    return await message.answer(text="Вернуться в главное меню", reply_markup=back_to_main_inline_btn)


# длина телеграм айди 9 символов - обработать ошибку
@dp.callback_query(F.data == "stats")
async def get_stats(callback: types.CallbackQuery):
    telegram_id = callback.from_user.id
    await callback.message.delete()

    if telegram_id not in ADMIN_IDS:
        return await callback.answer(
            "Это команда только для админа!",
            reply_markup=back_to_main_inline_btn
        )

    async with async_session_maker() as session:
        stats = await InviterService.get_all(session=session)

    if not stats:
        await callback.message.answer(
            "Нет инвайтеров.",
            reply_markup=back_to_main_inline_btn
        )
        return await callback.answer()

    text = "🧾 <b>Список инвайтеров</b>:\n"
    for stat in stats:
        text += (
            f"\n<b>🎯 Код:</b> <code>{stat.ref_code}</code>\n"
            f"👤 Пользователь: @{stat.username}\n"
            f"📲 Переходов: <b>{stat.click_count}</b>\n"
            f"🛠️ Создан: {stat.created_at.strftime('%d.%m.%Y')}\n"
            f"📅 Действует до: "
            f"{(stat.created_at + timedelta(days=stat.expire_time)).strftime('%d.%m.%Y')}\n"
            "──────────────"
        )

    await callback.message.answer(
        text,
        parse_mode="HTML",
        reply_markup=back_to_main_inline_btn
    )
    return await callback.answer()


@dp.callback_query(F.data == "mystats")
async def get_my_stats(callback: types.CallbackQuery):
    from bot.service import InviterService
    telegram_id = callback.from_user.id
    await callback.message.delete()
    if telegram_id in ADMIN_IDS:
        await callback.answer(
            "Это команда для пользователей!"
        )
        return await callback.answer()
    async with async_session_maker() as session:
        exists_inviter = await InviterService.get_one_or_none(
            session=session,
            telegram_id=telegram_id
        )
        if not exists_inviter:
            await callback.message.answer(
                f"Вы еще не являетесь инвайтером, обратитесь к админу в чате - {CHAT_LINK}.",
                reply_markup=back_to_main_inline_btn
            )
            return await callback.answer()

        stats = await InviterService.get_all(
            session=session,
            telegram_id=telegram_id
        )
        if not stats:
            await callback.message.answer("Нет готовых QR кодов.")
            return await callback.answer()
        text = "🧾 <b>Моя статистика</b>:\n"
        for stat in stats:
            text += (
                f"\n<b>🎯 Код:</b> <code>{stat.ref_code}</code>\n"
                f"👤 Пользователь: @{stat.username}\n"
                f"📲 Переходов: <b>{stat.click_count}</b>\n"
                f"🛠️ Создан: {stat.created_at.strftime('%d.%m.%Y')}\n"
                f"📅 Действует до: "
                f"{(stat.created_at + timedelta(days=stat.expire_time)).strftime('%d.%m.%Y')}\n"
                "──────────────"
            )

        await callback.message.answer(text, parse_mode="HTML", reply_markup=back_to_main_inline_btn)
        return await callback.answer()


@dp.callback_query(F.data == "myid")
async def get_my_telegram_id(callback: types.CallbackQuery):
    get_id = callback.from_user.id
    await callback.message.delete()
    await callback.message.answer(
        f"Ваш Telegram ID - <code>{get_id}</code>",
        parse_mode="HTML",
        reply_markup=back_to_main_inline_btn
    )
    return await callback.answer()


@dp.callback_query(lambda c: c.data == "back_to_main")
async def back_to_main_menu(callback: types.CallbackQuery):
    telegram_id = callback.from_user.id
    username = callback.from_user.username
    if telegram_id in ADMIN_IDS:
        await callback.message.edit_text(
            "👨‍💼 Привет, админ!\n"
            "🔹 Здесь ты может создавать новые куар коды и просматривать статистику по ним.\n"
            "Для этого выбери команду:",
            reply_markup=main_admin_inline_keyboard
        )
    else:
        await callback.message.edit_text(
            f"👋 С возвращением, @{username}!\n"
            f"Выберите команду:",
            reply_markup=main_user_inline_keyboard
        )
    await callback.answer()


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
