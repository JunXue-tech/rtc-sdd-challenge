import sys
import tempfile
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from sync_registered_teams import extract_team_names, update_file


class SyncRegisteredTeamsTests(unittest.TestCase):
    def test_extract_preserves_order_spacing_and_duplicates(self):
        rows = [
            ["Description"],
            ["Team name"],
            ["Team A "],
            [],
            [" Team B"],
            ["Team A "],
        ]
        self.assertEqual(
            extract_team_names(rows), ["Team A ", " Team B", "Team A "]
        )

    def test_extract_rejects_bad_or_empty_data(self):
        with self.assertRaises(ValueError):
            extract_team_names([["Description"], ["Other"], ["Team A"]])
        with self.assertRaises(ValueError):
            extract_team_names([["Description"], ["Team name"]])
        with self.assertRaises(ValueError):
            extract_team_names([["Description"], ["Team name"], ["A\nB"]])

    def test_file_changes_only_when_names_change(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "registered-teams.txt"
            path.write_text("# updatedAt: 2026-10-19\n\nTeam A\n", encoding="utf-8")
            self.assertFalse(update_file(path, ["Team A"], "2026-10-20"))
            self.assertTrue(update_file(path, ["Team A", "Team B"], "2026-10-20"))
            self.assertEqual(
                path.read_text(encoding="utf-8"),
                "# updatedAt: 2026-10-20\n\nTeam A\nTeam B\n",
            )


if __name__ == "__main__":
    unittest.main()
