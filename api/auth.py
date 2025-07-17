import hmac
import hashlib

from config import BOT_AUTH_TOKEN


def verify_telegram_auth(data: dict) -> bool:
    received_hash = data.get("hash")
    if not received_hash:
        return False

    # Убираем hash и все НЕ-Telegram поля
    auth_data = {k: v for k, v in data.items() if k != "hash" and k != "ref_code"}

    data_check_arr = [f"{k}={v}" for k, v in sorted(auth_data.items())]
    data_check_string = "\n".join(data_check_arr)

    secret_key = hashlib.sha256(BOT_AUTH_TOKEN.encode()).digest()
    hmac_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()

    return hmac.compare_digest(hmac_hash, received_hash)

