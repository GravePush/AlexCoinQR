from datetime import timedelta

from aiogram import F, types, Router
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

from bot.keyboards import back_to_main_inline_btn, main_admin_inline_keyboard, main_user_inline_keyboard
from bot.service import VisitorService, InviterService
from bot.utils import generate_ref_code, generate_and_send_qr
from config import ADMIN_IDS
from config import CHAT_LINK
from database import async_session_maker

router = Router()


@router.message(Command("start"))
async def handle_start(message: Message):
    args = message.text.split()
    ref_code = args[1] if len(args) > 1 else None
    telegram_id = message.from_user.id
    username = message.from_user.username

    if str(telegram_id) in ADMIN_IDS:
        return await message.answer(
            "<b>👨‍💼 Привет, админ!</b>\n\n"
            "🔹 <i>Здесь ты можешь создавать новые QR-коды и просматривать статистику по ним.</i>\n\n"
            "📊 <b>Статистика</b> — посмотреть статистику по всем инвайтерам.\n"
            "🤖 <b>Новый QR-код</b> — создать новый QR-код, бот пошагово попросит ввести:\n"
            "    • <code>Telegram ID</code> пользователя\n"
            "    • <code>Username</code> пользователя, которому создаёшь код (он сможет узнать свой ID по кнопке Мой Telegram ID).\n\n"
            "<i>Используй кнопки ниже для удобства работы.</i>",
            parse_mode="HTML",
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
            if inviter.telegram_id == telegram_id:
                return await message.answer(f"{username} вы перешли по своему куар коду.",
                                            reply_markup=main_user_inline_keyboard)
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


@router.callback_query(lambda c: c.data == "back_to_main")
async def back_to_main_menu(callback: types.CallbackQuery):
    telegram_id = callback.from_user.id
    username = callback.from_user.username
    if str(telegram_id) in ADMIN_IDS:
        await callback.message.edit_text(
            "<b>👨‍💼 Привет, админ!</b>\n\n"
            "🔹 <i>Здесь ты можешь создавать новые QR-коды и просматривать статистику по ним.</i>\n\n"
            "📊 <b>Статистика</b> — посмотреть статистику по всем инвайтерам.\n"
            "🤖 <b>Новый QR-код</b> — создать новый QR-код, бот пошагово попросит ввести:\n"
            "    • <code>Telegram ID</code> пользователя\n"
            "    • <code>Username</code> пользователя, которому создаёшь код (он сможет узнать свой ID по кнопке Мой Telegram ID).\n\n"
            "<i>Используй кнопки ниже для удобства работы.</i>",
            parse_mode="HTML",
            reply_markup=main_admin_inline_keyboard
        )
    else:
        await callback.message.edit_text(
            f"👋 С возвращением, @{username}!\n"
            f"Выберите команду:",
            reply_markup=main_user_inline_keyboard
        )
    await callback.answer()


@router.callback_query(F.data == "mystats")
async def get_my_stats(callback: types.CallbackQuery):
    from bot.service import InviterService
    telegram_id = callback.from_user.id
    await callback.message.delete()
    if str(telegram_id) in ADMIN_IDS:
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


@router.message(F.data == "myid")
async def get_my_telegram_id(callback: types.CallbackQuery):
    get_id = callback.from_user.id
    await callback.message.delete()
    await callback.message.answer(
        f"Ваш Telegram ID - <code>{get_id}</code>",
        parse_mode="HTML",
        reply_markup=back_to_main_inline_btn
    )
    return await callback.answer()


@router.callback_query(F.data == "qr")
async def create_qr(callback: CallbackQuery):
    telegram_id = callback.from_user.id
    username = callback.from_user.username
    async with async_session_maker() as session:
        exists_inviter = await InviterService.get_one_or_none(
            session=session,
            telegram_id=telegram_id
        )
    if exists_inviter:
        await callback.answer(f"У вас уже есть куар код!")
    await generate_and_send_qr(
        message=callback.message,
        telegram_id=telegram_id,
        username=username
    )
    await callback.answer()
