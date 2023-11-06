import json
from google.oauth2 import service_account
import gspread
from helper import get_config

__cfg = get_config().get("faq", {})
GSHEET_URL = __cfg.get("gsheet_url")


async def get_sheet():
    f = open("sherp-service-account-key.json", "r")
    service_account_key = json.load(f)
    f.close()

    credentials = service_account.Credentials.from_service_account_info(
        service_account_key
    )
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive",
    ]
    creds_with_scope = credentials.with_scopes(scope)
    client = gspread.authorize(creds_with_scope)

    spreadsheet = client.open_by_url(GSHEET_URL)
    sheet = spreadsheet.sheet1

    return sheet
