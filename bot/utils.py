import random
import string
from datetime import datetime, timezone, timedelta
from io import BytesIO

import qrcode
from aiogram.types import Message, BufferedInputFile

from bot.keyboards import back_to_main_inline_btn
from bot.service import InviterService
from config import DOMAIN
from database import async_session_maker


def generate_ref_code(length=8):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))


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
