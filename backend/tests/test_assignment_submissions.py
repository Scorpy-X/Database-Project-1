import unittest
from datetime import date
from unittest.mock import patch

from backend import app as vle_app


class FakeCursor:
    def __init__(self):
        self.executed = []

    def execute(self, query, params=None):
        self.executed.append((query, params))

    def fetchall(self):
        return [
            {
                "subID": 12,
                "userID": 620000000,
                "fname": "Danielle",
                "lname": "Johnson",
                "subText": "Submitted answer",
                "subContent": None,
                "submDate": date(2026, 5, 18),
                "grade": None,
            }
        ]

    def close(self):
        pass


class FakeConnection:
    def __init__(self):
        self.cursor_instance = FakeCursor()

    def cursor(self, dictionary=False):
        return self.cursor_instance

    def close(self):
        pass


class AssignmentSubmissionRouteTests(unittest.TestCase):
    def setUp(self):
        vle_app.app.config["TESTING"] = True
        self.client = vle_app.app.test_client()

    def test_course_manager_can_read_assignment_submissions(self):
        fake_connection = FakeConnection()

        with patch.object(vle_app, "require_basic_auth", return_value=({"accessLvl": "lecturer", "userID": 200000000}, None)), \
             patch.object(vle_app, "get_section_item_submission_context", return_value={"itemtype": "assignment", "courseCode": "COMP3161"}), \
             patch.object(vle_app, "can_manage_course", return_value=True), \
             patch.object(vle_app, "get_db_connection", return_value=fake_connection):
            response = self.client.get("/assignments/44/submissions")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), [
            {
                "subID": 12,
                "userID": 620000000,
                "fname": "Danielle",
                "lname": "Johnson",
                "subText": "Submitted answer",
                "subContent": None,
                "submDate": "2026-05-18",
                "grade": None,
            }
        ])


if __name__ == "__main__":
    unittest.main()
