"""Copy registered team names from the private Google Sheet into the site data file."""

import json
import os
from datetime import datetime
from pathlib import Path
from urllib.parse import quote
from zoneinfo import ZoneInfo


SPREADSHEET_ID = "1d4bjkUaHEFjicCVQBoTzgkTty-3QL3zvSyj9GsFjubs"
SHEET_RANGE = "Sheet3!A1:A"
TARGET = Path(__file__).resolve().parents[1] / "data" / "registered-teams.txt"
SCOPE = "https://www.googleapis.com/auth/spreadsheets.readonly"


def fetch_rows():
    key = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON")
    if not key:
        raise RuntimeError("Missing GOOGLE_SERVICE_ACCOUNT_JSON repository secret")

    from google.auth.transport.requests import AuthorizedSession
    from google.oauth2 import service_account

    credentials = service_account.Credentials.from_service_account_info(
        json.loads(key), scopes=[SCOPE]
    )
    url = (
        f"https://sheets.googleapis.com/v4/spreadsheets/{SPREADSHEET_ID}/values/"
        f"{quote(SHEET_RANGE, safe='')}"
    )
    response = AuthorizedSession(credentials).get(
        url, params={"valueRenderOption": "FORMATTED_VALUE"}, timeout=30
    )
    response.raise_for_status()
    return response.json().get("values", [])


def extract_team_names(rows):
    if len(rows) < 2 or not rows[1] or rows[1][0].strip() != "Team name":
        raise ValueError("Unexpected Sheet3 header; refusing to replace the team list")

    names = []
    for row in rows[2:]:
        name = row[0] if row else ""
        if not name.strip():
            continue
        if "\n" in name or "\r" in name or name.strip().startswith("#"):
            raise ValueError("Team name cannot be represented in registered-teams.txt")
        names.append(name)

    if not names:
        raise ValueError("No team names found; refusing to clear the team list")
    return names


def update_file(path, names, updated_at):
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or not lines[0].startswith("# updatedAt: "):
        raise ValueError("Unexpected registered-teams.txt format")
    current_names = [line for line in lines[1:] if line]
    if current_names == names:
        return False

    path.write_text(
        f"# updatedAt: {updated_at}\n\n" + "\n".join(names) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return True


def main():
    names = extract_team_names(fetch_rows())
    today = datetime.now(ZoneInfo("Asia/Shanghai")).date().isoformat()
    changed = update_file(TARGET, names, today)
    print(f"{'Updated' if changed else 'Unchanged'}: {len(names)} teams")


if __name__ == "__main__":
    main()
