import os
import json
import gspread

def test():
    sa = json.loads(os.environ["GOOGLE_SERVICE_ACCOUNT_JSON"])
    gc = gspread.service_account_from_dict(sa)
    sh = gc.open_by_key(os.environ["SHEET_ID"])
    ws = sh.worksheet("Sheet1")
    ws.append_row([1, 1, 1])
    print("OK: row appended to Sheet1")

test()
