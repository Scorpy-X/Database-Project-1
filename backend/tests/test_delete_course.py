import unittest
from unittest.mock import patch

from backend import app as vle_app


class FakeCursor:
    def __init__(self):
        self.statements = []
        self.closed = False

    def execute(self, query, params=None):
        self.statements.append((query, params))

    def close(self):
        self.closed = True


class FakeConnection:
    def __init__(self):
        self.cursor_instance = FakeCursor()
        self.committed = False
        self.rolled_back = False
        self.closed = False

    def cursor(self, dictionary=False):
        return self.cursor_instance

    def commit(self):
        self.committed = True

    def rollback(self):
        self.rolled_back = True

    def close(self):
        self.closed = True


class DeleteCourseRouteTests(unittest.TestCase):
    def setUp(self):
        vle_app.app.config["TESTING"] = True
        self.client = vle_app.app.test_client()

    def test_admin_can_delete_existing_course(self):
        fake_connection = FakeConnection()

        with patch.object(vle_app, "require_basic_auth", return_value=({"accessLvl": "admin"}, None)), \
             patch.object(vle_app, "course_exists", return_value=True), \
             patch.object(vle_app, "get_db_connection", return_value=fake_connection):
            response = self.client.delete("/courses/COMP3161")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {
            "message": "Course deleted successfully",
            "courseCode": "COMP3161",
        })
        self.assertTrue(fake_connection.committed)
        self.assertIn(
            ("DELETE FROM Course WHERE courseCode = %s", ("COMP3161",)),
            fake_connection.cursor_instance.statements,
        )

    def test_non_admin_cannot_delete_course(self):
        with patch.object(vle_app, "require_basic_auth", return_value=({"accessLvl": "student"}, None)):
            response = self.client.delete("/courses/COMP3161")

        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.get_json(), {"error": "Admin access required"})


if __name__ == "__main__":
    unittest.main()
