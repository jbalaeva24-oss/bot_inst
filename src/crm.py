"""Отправка лида в CRM через вебхук (Zapier / Make / n8n)."""
import logging
import aiohttp
import config

logger = logging.getLogger(__name__)


async def push_to_crm(lead_id: int, user_id: int, username: str | None,
                      full_name: str | None, answers: dict, utm: dict) -> None:
    if not config.CRM_WEBHOOK_URL:
        return
    payload = {
        "lead_id": lead_id,
        "user_id": user_id,
        "username": username or "",
        "full_name": full_name or "",
        "telegram_link": f"https://t.me/{username}" if username else "",
        **answers,
        **utm,
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(config.CRM_WEBHOOK_URL, json=payload, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status >= 400:
                    logger.warning("CRM webhook returned %s", resp.status)
    except Exception as e:
        logger.warning("CRM webhook failed: %s", e)
