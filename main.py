import sys
from datetime import datetime, timezone

from parser import fetch_prices
from exchange import get_usd_rate
from sheets import append_prices, append_errors, get_min_prices
from notifier import send, format_report


def main():
    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")

    print("Fetching prices from hotline.ua...")
    prices, errors = fetch_prices()
    print(f"  {len(prices)} prices ok, {len(errors)} errors")

    print("Fetching USD rate from minfin.com.ua...")
    usd_rate = get_usd_rate()
    if usd_rate is None:
        print("  WARNING: failed to fetch USD rate", file=sys.stderr)
    else:
        print(f"  Rate: {usd_rate}")

    print("Fetching historical minimums from Sheets...")
    try:
        historical_mins = get_min_prices()
    except Exception as e:
        print(f"  Sheets read error: {e}", file=sys.stderr)
        historical_mins = {}
    
    for p in prices:
        p["price_usd"] = round(p["price_uah"] / usd_rate, 2) if usd_rate else None

    by_size = {}
    sheet_rows = []
    for size in ("13", "15"):
        group = [p for p in prices if p["size"] == size]
        if not group:
            print(f"  WARNING: no prices found for {size}\"", file=sys.stderr)
            by_size[size] = None
            continue
        best = min(group, key=lambda x: x["price_uah"])
        by_size[size] = best
        sheet_rows.append({
            "size": size,
            "timecheck": now,
            "min_price_uah": best["price_uah"],
            "usd_rate": usd_rate,
            "min_price_usd": best.get("price_usd"),
            "model_code": f"{best['color']} {best['specs']}",
            "model_specs": best["specs"],
        })

    print("Sending Telegram notification...")
    msg = format_report(by_size, usd_rate, date_str, historical_mins)
    try:
        send(msg)
    except Exception as e:
        print(f"  Telegram error: {e}", file=sys.stderr)
    print(msg)
    
    print("Writing to Google Sheets...")
    try:
        append_prices(sheet_rows)
        append_errors(errors)
        print("  Sheets updated.")
    except Exception as e:
        print(f"  Sheets error: {type(e).__name__}: {e!r}", file=sys.stderr)


if __name__ == "__main__":
    main()
