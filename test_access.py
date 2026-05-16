import sys
from curl_cffi import requests as cf_requests

URL = (
    "https://hotline.ua/ua/computer-noutbuki-netbuki/"
    "apple-macbook-air-136-2026-apple-m5-8-core-gpu-16gb-512gb-silver/"
)

resp = cf_requests.get(
    URL,
    impersonate="chrome124",
    headers={
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "uk-UA,uk;q=0.9,en;q=0.8",
        "Referer": "https://hotline.ua/ua/",
    },
    timeout=30,
)

cf_blocked = "Just a moment" in resp.text
has_price = "грн" in resp.text or "₴" in resp.text

print(f"Status:          {resp.status_code}")
print(f"Response size:   {len(resp.text)} chars")
print(f"CF challenge:    {cf_blocked}")
print(f"Has price (грн/₴): {has_price}")

if resp.status_code == 200 and not cf_blocked and has_price:
    print("\n✅ ACCESS OK — curl_cffi bypasses Cloudflare from GitHub Actions")
    sys.exit(0)
else:
    print("\n❌ ACCESS FAILED — Cloudflare is blocking GitHub Actions IPs")
    sys.exit(1)
