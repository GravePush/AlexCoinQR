# import uvicorn
# from fastapi import FastAPI, Request, Depends, Form, HTTPException, Query
# from fastapi.responses import HTMLResponse, RedirectResponse
# from sqlalchemy.ext.asyncio import AsyncSession
# from sqlalchemy.future import select
# from starlette.templating import Jinja2Templates
#
# from api.auth import verify_telegram_auth
# from api.service import VisitorService
# from bot.service import InviterService
# from database import get_db
# from bot.models import InviterModel  # твоя модель с реф-кодами
# from api.models import VisitorModel  # твоя модель для посетителей
# from datetime import datetime, timezone
# import hashlib
# import hmac
#
# from config import BOT_AUTH_TOKEN, BOT_API, CHAT_LINK, DOMAIN
#
# app = FastAPI()
# templates = Jinja2Templates(directory="src/templates")  # Папка с HTML-шаблонами
#
# # @app.get("/ref")
# # async def get_info_ref(
# #         request: Request
# # ):
# #     return request.url
#
# # Конфиг Telegram бота
# BOT_USERNAME = "alexcoinauth_bot"
# BOT_TOKEN = BOT_AUTH_TOKEN
# TELEGRAM_GROUP_LINK = CHAT_LINK  # куда редиректить после входа
#
#
# # def check_telegram_auth(data: dict, bot_token: str) -> bool:
# #     """Проверка данных, пришедших из Telegram Login Widget"""
# #     auth_data = data.copy()
# #     check_hash = auth_data.pop("hash", None)
# #     if not check_hash:
# #         return False
# #
# #     data_check_arr = [f"{k}={v}" for k, v in sorted(auth_data.items())]
# #     data_check_string = "\n".join(data_check_arr).encode('utf-8')
# #
# #     secret_key = hashlib.sha256(bot_token.encode('utf-8')).digest()
# #     hmac_hash = hmac.new(secret_key, data_check_string, hashlib.sha256).hexdigest()
# #
# #     return hmac_hash == check_hash
#
#
# @app.get("/ref/{ref_code}", response_class=HTMLResponse)
# async def show_telegram_login(request: Request, ref_code: str, session: AsyncSession = Depends(get_db)):
#     # Проверяем, есть ли такой реферальный код
#     inviter = await InviterService.get_one_or_none(session, ref_code=ref_code)
#     if not inviter:
#         return HTMLResponse("Неверный реферальный код", status_code=400)
#
#     # Отдаем страницу с Telegram Login Widget и передаем ref_code в форму (чтобы потом знать, чей это приглашенный)
#     return templates.TemplateResponse("index.html", {"request": request, "ref_code": ref_code})
#
#
# @app.get("/auth/telegram")
# async def telegram_auth(
#     request: Request,
#     id: str = Query(...),
#     first_name: str = Query(...),
#     last_name: str = Query(...),
#     username: str = Query(...),
#     auth_date: str = Query(...),
#     photo_url: str = Query(...),
#     hash: str = Query(...),
#     ref_code: str = Query(...),
#     session: AsyncSession = Depends(get_db)
# ):
#
#     data = {
#         "id": id,
#         "first_name": first_name,
#         "last_name": last_name,
#         "username": username,
#         "auth_date": auth_date,
#         "photo_url": photo_url,
#         "hash": hash
#     }
#     print(data)
#     # Проверяем подпись
#     if not verify_telegram_auth(data):
#         raise HTTPException(status_code=400, detail="Invalid Telegram auth data!!!!")
#
#     # Проверяем реферальный код
#     inviter = await InviterService.get_one_or_none(session, ref_code=ref_code)
#     if not inviter:
#         raise HTTPException(status_code=400, detail="Invalid ref code")
#
#     # Проверяем, есть ли уже такой пользователь
#     visitor = await VisitorService.get_one_or_none(session, telegram_id=int(id))
#     if not visitor:
#         # Создаем нового посетителя
#         new_visitor = VisitorModel(
#             ref_code=ref_code,
#             username=username,
#             telegram_id=int(id),
#             created_at=datetime.now(timezone.utc),
#             inviter_id=inviter.id
#         )
#         session.add(new_visitor)
#         inviter.click_count += 1
#         await session.commit()
#
#
#     # Можно редиректить в группу или на страницу успеха
#     return RedirectResponse(url=CHAT_LINK, status_code=302)
#
#
# # @app.get("/ref/{ref_code}")
# # async def redirect_by_ref(
# #         ref_code: str,
# #         request: Request,
# #         session: AsyncSession = Depends(get_db)
# # ):
#
# # return templates.TemplateResponse("index.html", {"request": request, "ref_code": ref_code})
# # inviter = await InviterService.get_one_or_none(
# #     session=session,
# #     ref_code=ref_code
# # )
# # if inviter:
# #     inviter.click_count += 1
# #
# #     await session.commit()
# #     return {
# #         "inviter": inviter,
# #         "QR code ref": ref_code
# #     }
# # return "Invalid ref!"
# # Достаём параметры Telegram Login Widget из query
# # query_params = dict(request.query_params)
# #
# # if not verify_telegram_auth(query_params.copy()):
# #     print(query_params)
# #     raise HTTPException(status_code=403, detail="Invalid Telegram login")
# #
# # telegram_id = int(query_params["id"])
# # username = query_params.get("username")
# #
# # # Проверка — есть ли уже такой пользователь
# # existing_visitor = await VisitorService.get_one_or_none(
# #     session=session,
# #     telegram_id=telegram_id
# # )
# #
# # if not existing_visitor:
# #     inviter = await InviterService.get_one_or_none(
# #         session=session,
# #         ref_code=ref_code
# #     )
# #
# #     new_visitor = VisitorModel(
# #         telegram_id=telegram_id,
# #         username=username,
# #         ref_code=ref_code,
# #         inviter_id=inviter.id
# #     )
# #     session.add(new_visitor)
# #
# #     if inviter:
# #         inviter.click_count += 1
# #
# # await session.commit()
# #
# # return RedirectResponse(url=CHAT_LINK)
#
#
# if __name__ == "__main__":
#     uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
