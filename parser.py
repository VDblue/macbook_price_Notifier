import re
import json
import time
from datetime import datetime, timezone
from curl_cffi import requests as cf_requests

_BASE = "https://hotline.ua/ua/computer-noutbuki-netbuki/"
_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "uk-UA,uk;q=0.9,en;q=0.8",
    "Referer": "https://hotline.ua/ua/",
}
_COLORS = ["silver", "starlight", "midnight", "sky-blue"]

# (size, gpu_slug, ram, storage)
_CONFIGS = [
    ("13", "apple-m5-8-core-gpu",  "16GB", "512GB"),
    ("13", "apple-m5-8-core-gpu",  "16GB", "1TB"),
    ("13", "apple-m5-10-core-gpu", "24GB", "512GB"),
    ("13", "apple-m5-10-core-gpu", "24GB", "1TB"),
    ("15", "apple-m5-10-core-gpu", "16GB", "512GB"),
    ("15", "apple-m5-10-core-gpu", "16GB", "1TB"),
    ("15", "apple-m5-10-core-gpu", "24GB", "512GB"),
    ("15", "apple-m5-10-core-gpu", "24GB", "1TB"),
]


def _build_products():
    products = []
    for size, gpu, ram, storage in _CONFIGS:
        size_slug = "136" if size == "13" else "15"
        specs = f"{ram}/{storage}"
        for color in _COLORS:
            slug = f"apple-macbook-air-{size_slug}-2026-{gpu}-{ram.lower()}-{storage.lower()}-{color}"
            products.append({
                "size": size,
                "specs": specs,
                "color": color.replace("-", " ").title(),
                "url": f"{_BASE}{slug}/",
            })
    return products


PRODUCTS = _build_products()


def _parse_price(html):
    for m in re.finditer(
        r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
        html, re.DOTALL,
    ):
        try:
            data = json.loads(m.group(1).strip())
            offers = data.get("offers") if isinstance(data, dict) else None
            if isinstance(offers, dict):
                low = offers.get("lowPrice") or offers.get("price")
                if low:
                    return int(float(low))
        except Exception:
            continue

    m = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', html, re.DOTALL)
    if m:
        try:
            data = json.loads(m.group(1))
            prices = []

            def walk(node):
                if isinstance(node, dict):
                    for k, v in node.items():
                        if any(h in k.lower() for h in ("price", "cost", "minprice", "lowprice")) \
                                and isinstance(v, (int, float)) and 20000 < v < 300000:
                            prices.append(int(v))
                        walk(v)
                elif isinstance(node, list):
                    for x in node:
                        walk(x)

            walk(data)
            if prices:
                return min(prices)
        except Exception:
            pass

    cand = []
    for m in re.finditer(r'(?:від|from)\s+(\d{2,3}(?:[\s ]\d{3})+)\s*[₴грн]', html):
        try:
            n = int(m.group(1).replace(" ", "").replace(" ", ""))
            if 20000 < n < 300000:
                cand.append(n)
        except Exception:
            continue
    return min(cand) if cand else None


def fetch_prices():
    results, errors = [], []
    fetched_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    for p in PRODUCTS:
        try:
            r = cf_requests.get(p["url"], impersonate="chrome124", headers=_HEADERS, timeout=30)
            if r.status_code != 200:
                errors.append({"url": p["url"], "error": f"HTTP {r.status_code}"})
            elif "Just a moment" in r.text:
                errors.append({"url": p["url"], "error": "CF challenge"})
            else:
                price = _parse_price(r.text)
                if price is None:
                    errors.append({"url": p["url"], "error": "price not found"})
                else:
                    results.append({**p, "price_uah": price, "fetched_at": fetched_at})
        except Exception as e:
            errors.append({"url": p["url"], "error": str(e)})
        time.sleep(2)
    return results, errors
