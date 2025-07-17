# import asyncio
# import uvicorn
# from bot.main import dp, bot
# from fastapi import FastAPI
# from api.main import app as api_app
#
# async def start_api():
#     """Запуск uvicorn сервера FastAPI в asyncio задаче"""
#     config = uvicorn.Config(api_app, host="127.0.0.1", port=8000, reload=False)
#     server = uvicorn.Server(config)
#     await server.serve()
#
# async def start_bot():
#     """Запуск Telegram бота (aiogram polling)"""
#     await dp.start_polling(bot)
#
# async def main():
#     await asyncio.gather(
#         start_api(),
#         start_bot()
#     )
#
# if __name__ == "__main__":
#     asyncio.run(main())
