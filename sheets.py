import os
import json
import gspread
from datetime import datetime, timezone

_PRICES_COLS = ["size", "timecheck", "min_price_uah", "usd_rate", "min_price_usd", "model_code", "model_specs"]
_ERRORS_COLS = ["timestamp", "url", "error"]


def _client():
    sa = json.loads(os.environ["GOOGLE_SERVICE_ACCOUNT_JSON"])
    return gspread.service_account_from_dict(sa)


def _worksheet(gc, tab_name, headers):
    sh = gc.open_by_key(os.environ["SHEET_ID"])
    try:
        return sh.worksheet(tab_name)
    except gspread.exceptions.WorksheetNotFound:
        ws = sh.add_worksheet(title=tab_name, rows=5000, cols=len(headers))
        ws.append_row(headers)
        return ws


def append_prices(rows):
    gc = _client()
    ws = _worksheet(gc, "prices", _PRICES_COLS)
    for r in rows:
        ws.append_row([
            r["size"],
            r["timecheck"],
            r["min_price_uah"],
            r.get("usd_rate") or "",
            r.get("min_price_usd") or "",
            r["model_code"],
            r["model_specs"],
        ])


def append_errors(errors):
    if not errors:
        return
    gc = _client()
    ws = _worksheet(gc, "errors", _ERRORS_COLS)
    ts = datetime.now(timezone.utc).isoformat(timespec="seconds")
    for e in errors:
        ws.append_row([ts, e["url"], e["error"]])
