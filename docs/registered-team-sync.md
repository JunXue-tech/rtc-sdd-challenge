# Registered team sync

The GitHub Actions workflow runs daily at 23:59 Asia/Shanghai and can also be
started manually from the repository's Actions tab. It reads `Sheet3` column A
from the private registration spreadsheet and updates `data/registered-teams.txt`
only when the names change.

## One-time setup

1. In a Google Cloud project, enable the Google Sheets API. Create a dedicated
   service account without project roles, then create a JSON key for it.
2. In the registration spreadsheet's Share dialog, add the service account's
   email address as a Viewer. The account currently connected to Codex is not
   used by GitHub Actions.
3. In the GitHub repository, open Settings > Secrets and variables > Actions and
   create the repository secret `GOOGLE_SERVICE_ACCOUNT_JSON` containing the
   entire JSON key. Do not commit the key or paste it into chat.
4. Run the workflow manually from Actions > Sync registered teams > Run workflow.
   Verify that it succeeds before pausing the existing local Codex schedule.

The workflow uses the repository's `GITHUB_TOKEN` with `contents: write` to push
only a changed team-list file. A failed Sheets read, invalid header, or empty
list stops the job before any commit or push. Service account keys are long-lived;
keep this account limited to Viewer access on the required spreadsheet and
rotate or remove the key when the sync is no longer needed.
