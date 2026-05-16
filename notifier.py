import os
import json
from urllib import request as urllib_request


def send(text):
    token = os.environ["TG_BOT_TOKEN"].strip()
    chat_id = os.environ["TG_CHAT_ID"].strip()
    payload = json.dumps({"chat_id": chat_id, "text": text, "parse_mode": "HTML"}).encode()
    req = urllib_request.Request(
        f"https://api.telegram.org/bot{token}/sendMessage",
        data=payload,
        headers={"Content-Type": "application/json"},
    )
    urllib_request.urlopen(req, timeout=15)


def format_report(by_size, usd_rate, date_str, historical_mins=None):
    lines = [f"<b>MacBook Air M5 — {date_str}</b>", ""]
    for size in ("13", "15"):
        data = by_size.get(size)
        hist_min = (historical_mins or {}).get(size)
        lines.append(f'<b>{size}"</b>')
        if data:
            uah = f"{data['price_uah']:,}".replace(",", " ")
            usd = f"  /  ${data['price_usd']:,.0f}".replace(",", " ") if data.get("price_usd") else ""
            lines.append(f"  {uah} ₴{usd}")
            lines.append(f"  {data['specs']}  {data['color']}")
            if hist_min:
                diff = today_usd - hist_min
                sign = "+" if diff >= 0 else "−"
                lines.append(f"  Min ever: ${hist_min:,.0f}  ({sign}${abs(diff):,.0f})")
            else:
                lines.append("  ціну не знайдено")
        lines.append("")
    if usd_rate:
        lines.append(f"Курс: 1 USD = {usd_rate:.2f} ₴ (готівка, minfin)")
    return "\n".join(lines)
