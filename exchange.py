import re
import json
from curl_cffi import requests as cf_requests

_URL = "https://minfin.com.ua/ua/currency/mb/"
_HEADERS = {
    "Accept-Language": "uk-UA,uk;q=0.9,en;q=0.8",
    "Referer": "https://minfin.com.ua/",
}


def get_usd_rate():
    try:
        resp = cf_requests.get(_URL, impersonate="chrome124", headers=_HEADERS, timeout=20)
        if resp.status_code != 200:
            return None
        html = resp.text

        m = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', html, re.DOTALL)
        if m:
            try:
                data = json.loads(m.group(1))
                candidates = []

                def walk(node):
                    if isinstance(node, dict):
                        cur = str(
                            node.get("currency") or node.get("code") or node.get("iso") or ""
                        ).upper()
                        if "USD" in cur:
                            for key in ("buy", "buyRate", "purchase", "bid"):
                                v = node.get(key)
                                if isinstance(v, (int, float)) and 30 < v < 65:
                                    candidates.append(float(v))
                        for v in node.values():
                            walk(v)
                    elif isinstance(node, list):
                        for x in node:
                            walk(x)

                walk(data)
                if candidates:
                    return candidates[0]
            except Exception:
                pass

        # fallback: USD context + numeric rate
        m = re.search(
            r'USD[^<]{0,300}?(3[5-9]\.\d{1,2}|4[0-9]\.\d{1,2}|5[0-4]\.\d{1,2})',
            html, re.DOTALL | re.IGNORECASE,
        )
        if m:
            val = float(m.group(1))
            if 30 < val < 65:
                return val
        return None
    except Exception:
        return None
