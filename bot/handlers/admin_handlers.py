from datetime import timedelta

from aiogram import F, types, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message

from bot.keyboards import back_to_main_inline_btn
from config import ADMIN_IDS
from bot.service import InviterService
from bot.utils import generate_and_send_qr
from database import async_session_maker

router = Router()


# class QRForm(StatesGroup):
#     telegram_id = State()
#     username = State()


# @router.callback_query(F.data == "newqr")
# async def start_process_qr(callback: types.CallbackQuery, state: FSMContext):
#     admin_telegram_id = callback.from_user.id
#     if str(admin_telegram_id) not in ADMIN_IDS:
#         await callback.message.answer(
#             "У вас нет доступа к этой команде!",
#             reply_markup=back_to_main_inline_btn
#         )
#         return await callback.answer()
#     await state.set_state(QRForm.telegram_id)
#     await callback.message.answer("Введите Telegram ID пользователя (числом):")
#     await callback.answer()
#
#
# @router.message(QRForm.telegram_id)
# async def process_telegram_id(message: Message, state: FSMContext):
#     if not message.text.isdigit():
#         return await message.answer("❌ Введите числовой Telegram ID.")
#
#     await state.update_data(telegram_id=int(message.text))
#     await message.answer("Теперь введите username пользователя:")
#     await state.set_state(QRForm.username)
#
#
# @router.message(QRForm.telegram_id)
# async def process_telegram_id(message: Message, state: FSMContext):
#     if not message.text.isdigit():
#         return await message.answer("❌ Введите числовой Telegram ID.")
#
#     await state.update_data(telegram_id=int(message.text))
#     await state.set_state(QRForm.username)
#     await message.answer("Теперь введите username:")
#
#
# @router.message(QRForm.username)
# async def process_username_and_finish_fsm(message: Message, state: FSMContext):
#     username = message.text.strip().lstrip("@")
#     await state.update_data(username=username)
#
#     data = await state.get_data()
#     await state.clear()
#
#     await generate_and_send_qr(
#         message=message,
#         telegram_id=data["telegram_id"],
#         username=data["username"]
#     )


@router.callback_query(F.data == "stats")
async def get_stats(callback: types.CallbackQuery):
    telegram_id = callback.from_user.id
    await callback.message.delete()

    if str(telegram_id) not in ADMIN_IDS:
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
        expire_date = stat.created_at + timedelta(days=stat.expire_time)
        text += (
            f"\n<b>🎯 Реферальный код:</b> <code>{stat.ref_code}</code>\n"
            f"👤 <b>Пользователь:</b> @{stat.username}\n"
            f"📲 <b>Переходов:</b> <b>{stat.click_count}</b>\n"
            f"🛠️ <b>Создан:</b> {stat.created_at.strftime('%d.%m.%Y')}\n"
            f"📅 <b>Действует до:</b> {expire_date.strftime('%d.%m.%Y')}\n"
            "\n"
        )

    await callback.message.answer(
        text,
        parse_mode="HTML",
        reply_markup=back_to_main_inline_btn
    )
    return await callback.answer()
