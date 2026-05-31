"""
Flask API for the COMP3161 VLE coursework project.

This file intentionally keeps the API in one place for group-project handoff.
Routes are grouped by feature area, while helpers above the routes centralize
validation, authentication, authorization, and common database lookups.
"""

import os
import hashlib
import re
import secrets
import string
from flask import Flask
from flask import request, jsonify
from flask_cors import CORS
from datetime import date, datetime
import mysql.connector
from dotenv import load_dotenv


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

app = Flask(__name__)
CORS(app, origins=["http://localhost:5173", "http://127.0.0.1:5173"])


# ---------------------------------------------------------------------------
# App setup and database connection
# ---------------------------------------------------------------------------

def get_db_connection():
    """Open a MySQL connection using values from .env, with local defaults."""
    connection = mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "Vle"),
    )
    return connection


def hash_password(password):
    """Return the full SHA-256 hex digest used by login and seed data."""
    return hashlib.sha256(password.encode()).hexdigest()


# ---------------------------------------------------------------------------
# Constants and project rules
# ---------------------------------------------------------------------------

PASSWORD_LENGTH = 10
PASSWORD_ALPHABET = string.ascii_letters
DUPLICATE_ENTRY_ERRNO = 1062
COURSE_CODE_PATTERN = re.compile(r"^[A-Z0-9]{8}$")

ROLE_ID_RANGES = {
    "student": (620000000, 620999999),
    "lecturer": (200000000, 200999999),
    "admin": (111000000, 111999999),
}

ALLOWED_DEPARTMENTS = (
    "Computer Science", "Mathematics", "Physics", "Chemistry", "Biology",
    "Engineering", "Economics", "Management", "Law", "Medicine",
    "Psychology", "Sociology", "History", "Literature", "Philosophy",
    "Agriculture", "Education", "Nursing", "Architecture", "Accounting",
)
DEPARTMENTS_BY_CASEFOLD = {department.casefold(): department for department in ALLOWED_DEPARTMENTS}
ALLOWED_ITEM_TYPES = {"assignment", "link", "file", "slide"}


# ---------------------------------------------------------------------------
# Validation helpers
# ---------------------------------------------------------------------------

def generate_password():
    """Generate the one-time returned permanent password for admin-created users."""
    return "".join(secrets.choice(PASSWORD_ALPHABET) for _ in range(PASSWORD_LENGTH))


def clean_required_string(value, field_name, max_len):
    """Trim and validate a required string field against the schema length."""
    if value is None:
        raise ValueError(f"{field_name} is required")
    if not isinstance(value, str):
        raise ValueError(f"{field_name} must be text")

    cleaned = value.strip()
    if not cleaned:
        raise ValueError(f"{field_name} is required")
    if len(cleaned) > max_len:
        raise ValueError(f"{field_name} must be {max_len} characters or fewer")
    return cleaned


def clean_optional_string(value, field_name, max_len):
    """Trim an optional string field and normalize blank strings to None."""
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValueError(f"{field_name} must be text")

    cleaned = value.strip()
    if len(cleaned) > max_len:
        raise ValueError(f"{field_name} must be {max_len} characters or fewer")
    return cleaned or None


def clean_required_text(value, field_name, max_len):
    return clean_required_string(value, field_name, max_len)


def clean_optional_text(value, field_name, max_len):
    return clean_optional_string(value, field_name, max_len)


def parse_required_int(value, field_name):
    """Parse required integer input while rejecting booleans and floats."""
    if value is None or str(value).strip() == "":
        raise ValueError(f"{field_name} is required")
    if isinstance(value, bool) or isinstance(value, float):
        raise ValueError(f"{field_name} must be an integer")
    try:
        return int(value)
    except (TypeError, ValueError):
        raise ValueError(f"{field_name} must be an integer")


def parse_optional_grade(value):
    """Validate an optional integer grade in the inclusive 0-100 range."""
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError("grade must be an integer between 0 and 100")
    if not 0 <= value <= 100:
        raise ValueError("grade must be an integer between 0 and 100")
    return value


def parse_required_grade(value):
    """Validate a required integer grade in the inclusive 0-100 range."""
    if value is None:
        raise ValueError("grade is required")
    return parse_optional_grade(value)


def parse_optional_date(value):
    """Parse an optional YYYY-MM-DD query parameter for filtering."""
    if value is None or value == "":
        return None
    if not isinstance(value, str):
        raise ValueError("date must use YYYY-MM-DD format")

    cleaned = value.strip()
    if not cleaned:
        return None

    try:
        parsed_date = datetime.strptime(cleaned, "%Y-%m-%d").date()
    except ValueError:
        raise ValueError("date must use YYYY-MM-DD format")
    return parsed_date.isoformat()


def parse_required_date(value, field_name):
    """Parse a required YYYY-MM-DD JSON field."""
    if value is None:
        raise ValueError(f"{field_name} is required")
    if not isinstance(value, str):
        raise ValueError(f"{field_name} must use YYYY-MM-DD format")

    cleaned = value.strip()
    if not cleaned:
        raise ValueError(f"{field_name} is required")

    try:
        parsed_date = datetime.strptime(cleaned, "%Y-%m-%d").date()
    except ValueError:
        raise ValueError(f"{field_name} must use YYYY-MM-DD format")
    return parsed_date.isoformat()


def parse_item_due_date(itemtype, value):
    """Allow dueDate only for assignment section items."""
    if value is None:
        return None
    if isinstance(value, str) and not value.strip():
        return None
    if itemtype != "assignment":
        raise ValueError("dueDate is only allowed for assignment items")
    try:
        return parse_required_date(value, "dueDate")
    except ValueError:
        raise ValueError("dueDate must use YYYY-MM-DD format")


def parse_optional_int(value, field_name):
    if value is None:
        return None
    return parse_required_int(value, field_name)


def clean_course_code(course_code):
    """Normalize and validate the required 8-character course code format."""
    cleaned = clean_required_string(course_code, "courseCode", 8).upper()
    if len(cleaned) != 8 or not COURSE_CODE_PATTERN.fullmatch(cleaned):
        raise ValueError("courseCode must be exactly 8 uppercase alphanumeric characters")
    return cleaned


def clean_item_type(value):
    """Validate the finite SectionItems.itemtype values used by the API."""
    itemtype = clean_required_string(value, "itemtype", 20).lower()
    if itemtype not in ALLOWED_ITEM_TYPES:
        raise ValueError("itemtype must be assignment, link, file, or slide")
    return itemtype


# ---------------------------------------------------------------------------
# Database lookup helpers
# ---------------------------------------------------------------------------

def validate_admin(cursor, admin_user_id):
    """Return True when the supplied userID belongs to an admin account."""
    cursor.execute(
        "SELECT userID FROM UserAccount WHERE userID = %s AND accessLvl = 'admin'",
        (admin_user_id,)
    )
    return cursor.fetchone() is not None


def get_next_user_id(cursor, access_lvl):
    """Find the next available userID inside the role-specific ID range."""
    start_id, end_id = ROLE_ID_RANGES[access_lvl]
    cursor.execute(
        "SELECT MAX(userID) AS max_id FROM UserAccount WHERE userID BETWEEN %s AND %s",
        (start_id, end_id)
    )
    result = cursor.fetchone()
    max_id = result["max_id"] if result else None
    next_id = start_id if max_id is None else max_id + 1

    if next_id > end_id:
        raise ValueError(f"No available {access_lvl} user IDs remain")
    return next_id


def parse_lecturer_id(value):
    return parse_required_int(value, "lecturerID")


def validate_lecturer(cursor, lecturer_id):
    """Return True when userID exists and belongs to a lecturer account."""
    cursor.execute(
        "SELECT userID FROM UserAccount WHERE userID = %s AND accessLvl = 'lecturer'",
        (lecturer_id,)
    )
    return cursor.fetchone() is not None


def course_exists(cursor, course_code):
    """Return True when a courseCode exists in Course."""
    cursor.execute("SELECT courseCode FROM Course WHERE courseCode = %s", (course_code,))
    return cursor.fetchone() is not None


def validate_student(cursor, user_id):
    """Return True when userID exists and belongs to a student account."""
    cursor.execute(
        "SELECT userID FROM UserAccount WHERE userID = %s AND accessLvl = 'student'",
        (user_id,)
    )
    return cursor.fetchone() is not None


def enrollment_exists(cursor, user_id, course_code):
    """Return True when the student is already enrolled in the course."""
    cursor.execute(
        "SELECT userID FROM Enrol WHERE userID = %s AND courseCode = %s",
        (user_id, course_code)
    )
    return cursor.fetchone() is not None


def get_section_item_submission_context(cursor, sec_item_id):
    """Fetch a section item's type and owning course for submission checks."""
    cursor.execute("""
        SELECT si.secItemID, si.itemtype, cs.courseCode
        FROM SectionItems si
        JOIN CourseSection cs ON si.secID = cs.secID
        WHERE si.secItemID = %s
    """, (sec_item_id,))
    return cursor.fetchone()


def get_section_course(cursor, sec_id):
    """Fetch a course section and the course it belongs to."""
    cursor.execute(
        "SELECT secID, secName, courseCode FROM CourseSection WHERE secID = %s",
        (sec_id,)
    )
    return cursor.fetchone()


def get_forum_course(cursor, df_id):
    """Fetch a discussion forum and its owning course."""
    cursor.execute(
        "SELECT dfID, courseCode FROM DiscussionForum WHERE dfID = %s",
        (df_id,)
    )
    return cursor.fetchone()


def get_thread_context(cursor, dt_id):
    """Fetch a discussion post's forum and course context."""
    cursor.execute("""
        SELECT dt.dtID, dt.dfID, df.courseCode
        FROM DiscussionThread dt
        JOIN DiscussionForum df ON dt.dfID = df.dfID
        WHERE dt.dtID = %s
    """, (dt_id,))
    return cursor.fetchone()


def get_discussion_post(cursor, dt_id):
    """Fetch one discussion post with author and course metadata."""
    cursor.execute("""
        SELECT
            dt.dtID,
            dt.dfID,
            df.courseCode,
            dt.parentpostID,
            dt.userID,
            ua.fname,
            ua.lname,
            dt.topic,
            dt.threadbody,
            dt.date_created
        FROM DiscussionThread dt
        JOIN DiscussionForum df ON dt.dfID = df.dfID
        JOIN UserAccount ua ON dt.userID = ua.userID
        WHERE dt.dtID = %s
    """, (dt_id,))
    return cursor.fetchone()


def serialize_discussion_post(row):
    """Convert a discussion row into the JSON shape returned by thread routes."""
    date_created = row["date_created"]
    if hasattr(date_created, "isoformat"):
        date_created = date_created.isoformat()

    return {
        "dtID": row["dtID"],
        "dfID": row["dfID"],
        "courseCode": row["courseCode"],
        "parentpostID": row.get("parentpostID"),
        "userID": row["userID"],
        "fname": row["fname"],
        "lname": row["lname"],
        "topic": row["topic"],
        "threadbody": row["threadbody"],
        "date_created": date_created,
        "replies": []
    }


def build_reply_tree(posts, root_id):
    """Build nested replies from flat DiscussionThread rows."""
    nodes = {post["dtID"]: serialize_discussion_post(post) for post in posts}

    for post in posts:
        parent_id = post["parentpostID"]
        if parent_id is not None and parent_id in nodes:
            nodes[parent_id]["replies"].append(nodes[post["dtID"]])

    return nodes.get(root_id)


def is_course_member(cursor, user_id, course_code):
    """Return True when a user appears in the CourseMember view for a course."""
    cursor.execute("""
        SELECT userID
        FROM CourseMember
        WHERE userID = %s AND courseCode = %s
    """, (user_id, course_code))
    return cursor.fetchone() is not None


# ---------------------------------------------------------------------------
# Authentication and authorization helpers
# ---------------------------------------------------------------------------

def get_basic_auth_user():
    """Authenticate Basic Auth credentials and return the matching user row."""
    auth = request.authorization
    if not auth or not auth.username or not auth.password:
        return None

    email = auth.username.strip().lower()
    if not email:
        return None

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT userID, email, accessLvl
            FROM UserAccount
            WHERE email = %s AND password = %s
        """, (email, hash_password(auth.password)))
        return cursor.fetchone()
    finally:
        cursor.close()
        conn.close()


def require_basic_auth():
    """Require Basic Auth and return either the user row or a 401 response."""
    user = get_basic_auth_user()
    if user:
        return user, None

    response = jsonify({"error": "Valid Basic Auth credentials required"})
    response.headers["WWW-Authenticate"] = 'Basic realm="VLE API"'
    return None, (response, 401)


def require_admin_user(user):
    """Return a 403 response unless the authenticated user is an admin."""
    if user["accessLvl"] != "admin":
        return jsonify({"error": "Admin access required"}), 403
    return None


def require_student_user(user):
    """Return a 403 response unless the authenticated user is a student."""
    if user["accessLvl"] != "student":
        return jsonify({"error": "Student access required"}), 403
    return None


def can_read_student_resource(user, target_user_id):
    """Allow admins or the target student to read student-owned resources."""
    if user["accessLvl"] == "admin":
        return True
    return user["accessLvl"] == "student" and user["userID"] == target_user_id


def can_read_lecturer_resource(user, target_user_id):
    """Allow admins or the target lecturer to read lecturer-owned resources."""
    if user["accessLvl"] == "admin":
        return True
    return user["accessLvl"] == "lecturer" and user["userID"] == target_user_id


def can_manage_course(cursor, user, course_code):
    """Allow admins or the assigned lecturer to manage a course."""
    if user["accessLvl"] == "admin":
        return True
    if user["accessLvl"] != "lecturer":
        return False

    cursor.execute("""
        SELECT userID
        FROM Teaches
        WHERE userID = %s AND courseCode = %s
    """, (user["userID"], course_code))
    return cursor.fetchone() is not None


def can_view_course(cursor, user, course_code):
    """Allow admins, assigned lecturers, or enrolled students to view a course."""
    if user["accessLvl"] == "admin":
        return True
    if user["accessLvl"] == "lecturer":
        return can_manage_course(cursor, user, course_code)
    if user["accessLvl"] != "student":
        return False

    cursor.execute("""
        SELECT userID
        FROM Enrol
        WHERE userID = %s AND courseCode = %s
    """, (user["userID"], course_code))
    return cursor.fetchone() is not None


def can_post_in_course(cursor, user, course_code):
    """Allow admins or course members to create forum threads and replies."""
    if user["accessLvl"] == "admin":
        return True
    return is_course_member(cursor, user["userID"], course_code)


# ---------------------------------------------------------------------------
# Course, calendar, and grading lookup helpers
# ---------------------------------------------------------------------------

def get_course_calendar(cursor, course_code):
    """Fetch the single CourseCalendar row for a course."""
    cursor.execute(
        "SELECT calendarID FROM CourseCalendar WHERE courseCode = %s",
        (course_code,)
    )
    return cursor.fetchone()


def get_submission_course(cursor, sub_id):
    """Find the course attached to a submission through its section item."""
    cursor.execute("""
        SELECT s.subID, s.userID, s.secItemID, cs.courseCode
        FROM Submission s
        JOIN SectionItems si ON s.secItemID = si.secItemID
        JOIN CourseSection cs ON si.secID = cs.secID
        WHERE s.subID = %s
    """, (sub_id,))
    return cursor.fetchone()


def recalculate_enrollment_grade(cursor, user_id, course_code):
    """Update Enrol.grade from the student's graded assignment submissions."""
    cursor.execute("""
        SELECT ROUND(AVG(s.grade)) AS courseGrade
        FROM Submission s
        JOIN SectionItems si ON s.secItemID = si.secItemID
        JOIN CourseSection cs ON si.secID = cs.secID
        WHERE s.userID = %s
          AND cs.courseCode = %s
          AND si.itemtype = 'assignment'
          AND s.grade IS NOT NULL
    """, (user_id, course_code))
    result = cursor.fetchone()
    course_grade = result["courseGrade"] if result else None
    if course_grade is not None:
        course_grade = int(course_grade)

    cursor.execute("""
        UPDATE Enrol
        SET grade = %s
        WHERE userID = %s AND courseCode = %s
    """, (course_grade, user_id, course_code))
    return course_grade


def get_course_lecturer(cursor, course_code):
    """Fetch the lecturer assigned to a course, if one exists."""
    cursor.execute(
        "SELECT userID FROM Teaches WHERE courseCode = %s",
        (course_code,)
    )
    return cursor.fetchone()

# ---------------------------------------------------------------------------
# Public test and user routes
# ---------------------------------------------------------------------------

# GET /api/data - public smoke-test endpoint for checking that Flask is running.
@app.route('/api/data')
def get_data():
    return jsonify({"message": "Hello world"})

if os.getenv("ENABLE_DEBUG_ROUTES") == "1":
    @app.route('/debug/tables', methods=['GET'])
    def debug_tables():
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SHOW TABLES")
            tables = [table[0] for table in cursor.fetchall()]
            cursor.close()
            conn.close()
            return jsonify({"database": "Vle", "tables": tables}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500


# GET /users - public user listing for demos; excludes password hashes.
@app.route('/users', methods=['GET']) 
def get_users():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True) 
    cursor.execute("SELECT userID, fname, lname, email, accessLvl FROM useraccount")
    users = cursor.fetchall() 
    cursor.close() 
    conn.close()
    return jsonify(users)


# POST /users/register - Basic Auth admin creates student, lecturer, or admin accounts.
@app.route("/users/register", methods=["POST"])
def register_user():
    user, auth_error = require_basic_auth()
    if auth_error:
        return auth_error
    admin_error = require_admin_user(user)
    if admin_error:
        return admin_error

    data = request.get_json(silent=True) or {}

    try:
        fname = clean_required_string(data.get("fname"), "fname", 50)
        lname = clean_required_string(data.get("lname"), "lname", 50)
        email = clean_required_string(data.get("email"), "email", 100).lower()
        access_lvl = clean_required_string(data.get("accessLvl"), "accessLvl", 20).lower()

        if "@" not in email or email.startswith("@") or email.endswith("@"):
            return jsonify({"error": "email must be a valid email address"}), 400
        if access_lvl not in ROLE_ID_RANGES:
            return jsonify({"error": "accessLvl must be student, lecturer, or admin"}), 400
    except ValueError as err:
        return jsonify({"error": str(err)}), 400

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("SELECT userID FROM UserAccount WHERE email = %s", (email,))
        if cursor.fetchone():
            return jsonify({"error": "Email already exists"}), 409

        user_id = get_next_user_id(cursor, access_lvl)
        generated_password = generate_password()
        cursor.execute("""
            INSERT INTO UserAccount (userID, fname, lname, email, accessLvl, password)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (user_id, fname, lname, email, access_lvl, hash_password(generated_password)))
        conn.commit()

        return jsonify({
            "message": "User registered successfully",
            "user": {
                "userID": user_id,
                "fname": fname,
                "lname": lname,
                "email": email,
                "accessLvl": access_lvl
            },
            "generatedPassword": generated_password
        }), 201
    except ValueError as err:
        conn.rollback()
        return jsonify({"error": str(err)}), 400
    except mysql.connector.Error as err:
        conn.rollback()
        if err.errno == DUPLICATE_ENTRY_ERRNO:
            return jsonify({"error": "User email or ID already exists"}), 409
        return jsonify({"error": str(err)}), 400
    finally:
        cursor.close()
        conn.close()


# POST /auth/login - public credential check used for demo login validation.
@app.route("/auth/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}

    try:
        email = clean_required_string(data.get("email"), "email", 100).lower()
        password = clean_required_string(data.get("password"), "password", 100)
    except ValueError as err:
        return jsonify({"error": str(err)}), 400

    hashed_password = hash_password(password)

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT userID, fname, lname, accessLvl FROM UserAccount WHERE email=%s AND password=%s",
                   (email, hashed_password))
    user = cursor.fetchone()
    cursor.close()
    conn.close()

    if user:
        return jsonify({"message": "Login successful", "user": user}), 200
    return jsonify({"error": "Invalid credentials"}), 401


# GET /users/{userID} - public profile read; excludes password hashes.
@app.route("/users/<int:userID>", methods=["GET"])
def get_user(userID):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT userID, fname, lname, email, accessLvl FROM UserAccount WHERE userID=%s", (userID,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()

    if user:
        return jsonify(user), 200
    return jsonify({"error": "User not found"}), 404


# ---------------------------------------------------------------------------
# Course, lecturer, and enrollment routes
# ---------------------------------------------------------------------------

# GET /courses - public course catalog for discovery and demos.
@app.route("/courses", methods=["GET"])
def list_courses():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT courseCode, courseName, department FROM Course")
    courses = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(courses), 200


# POST /courses - Basic Auth admin creates a course shell and assigns one lecturer.
@app.route("/courses", methods=["POST"])
def create_course():
    user, auth_error = require_basic_auth()
    if auth_error:
        return auth_error
    admin_error = require_admin_user(user)
    if admin_error:
        return admin_error

    data = request.get_json(silent=True) or {}

    try:
        course_code = clean_course_code(data.get("courseCode"))
        course_name = clean_required_string(data.get("courseName"), "courseName", 50)
        department_input = clean_required_string(data.get("department"), "department", 50)
        lecturer_id = parse_lecturer_id(data.get("lecturerID"))

        department = DEPARTMENTS_BY_CASEFOLD.get(department_input.casefold())
        if department is None:
            return jsonify({"error": "department must be one of the supported departments"}), 400
    except ValueError as err:
        return jsonify({"error": str(err)}), 400

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        if not validate_lecturer(cursor, lecturer_id):
            return jsonify({"error": "lecturerID must belong to a lecturer user"}), 400

        cursor.execute(
            "SELECT courseCode, courseName FROM Course WHERE courseCode = %s OR courseName = %s",
            (course_code, course_name)
        )
        existing_course = cursor.fetchone()
        if existing_course:
            if existing_course["courseCode"] == course_code:
                return jsonify({"error": "Course code already exists"}), 409
            return jsonify({"error": "Course name already exists"}), 409

        cursor.execute("""
            INSERT INTO Course (courseCode, courseName, department)
            VALUES (%s, %s, %s)
        """, (course_code, course_name, department))

        cursor.execute("""
            INSERT INTO Teaches (userID, courseCode)
            VALUES (%s, %s)
        """, (lecturer_id, course_code))

        cursor.execute("INSERT INTO CourseCalendar (courseCode) VALUES (%s)", (course_code,))
        calendar_id = cursor.lastrowid

        cursor.execute("""
            INSERT INTO DiscussionForum (dfname, courseCode)
            VALUES (%s, %s)
        """, ("General Discussion", course_code))
        df_id = cursor.lastrowid

        cursor.execute("""
            INSERT INTO CourseSection (secName, courseCode)
            VALUES (%s, %s)
        """, ("Course Overview", course_code))
        sec_id = cursor.lastrowid

        conn.commit()

        return jsonify({
            "message": "Course created successfully",
            "course": {
                "courseCode": course_code,
                "courseName": course_name,
                "department": department
            },
            "lecturerID": lecturer_id,
            "defaults": {
                "calendarID": calendar_id,
                "dfID": df_id,
                "secID": sec_id
            }
        }), 201
    except ValueError as err:
        conn.rollback()
        return jsonify({"error": str(err)}), 400
    except mysql.connector.Error as err:
        conn.rollback()
        if err.errno == DUPLICATE_ENTRY_ERRNO:
            return jsonify({"error": "Course code or name already exists"}), 409
        return jsonify({"error": str(err)}), 400
    finally:
        cursor.close()
        conn.close()


# DELETE /courses/{courseCode} - Basic Auth admin deletes a course and cascades dependents.
@app.route("/courses/<string:courseCode>", methods=["DELETE"])
def delete_course(courseCode):
    user, auth_error = require_basic_auth()
    if auth_error:
        return auth_error
    admin_error = require_admin_user(user)
    if admin_error:
        return admin_error

    try:
        normalized_course_code = clean_course_code(courseCode)
    except ValueError as err:
        return jsonify({"error": str(err)}), 400

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        if not course_exists(cursor, normalized_course_code):
            return jsonify({"error": "Course not found"}), 404

        cursor.execute("DELETE FROM Course WHERE courseCode = %s", (normalized_course_code,))
        conn.commit()

        return jsonify({
            "message": "Course deleted successfully",
            "courseCode": normalized_course_code
        }), 200
    except mysql.connector.Error as err:
        conn.rollback()
        return jsonify({"error": str(err)}), 400
    finally:
        cursor.close()
        conn.close()


# PUT /courses/{courseCode}/lecturer - Basic Auth admin replaces a course lecturer.
@app.route("/courses/<string:courseCode>/lecturer", methods=["PUT"])
def assign_course_lecturer(courseCode):
    user, auth_error = require_basic_auth()
    if auth_error:
        return auth_error
    admin_error = require_admin_user(user)
    if admin_error:
        return admin_error

    data = request.get_json(silent=True) or {}

    try:
        normalized_course_code = clean_course_code(courseCode)
        lecturer_id = parse_lecturer_id(data.get("lecturerID"))
    except ValueError as err:
        return jsonify({"error": str(err)}), 400

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        if not course_exists(cursor, normalized_course_code):
            return jsonify({"error": "Course not found"}), 404

        if not validate_lecturer(cursor, lecturer_id):
            return jsonify({"error": "lecturerID must belong to a lecturer user"}), 400

        existing_assignment = get_course_lecturer(cursor, normalized_course_code)
        if existing_assignment and existing_assignment["userID"] == lecturer_id:
            return jsonify({
                "message": "Lecturer is already assigned to this course",
                "courseCode": normalized_course_code,
                "lecturerID": lecturer_id
            }), 200

        cursor.execute("DELETE FROM Teaches WHERE courseCode = %s", (normalized_course_code,))
        cursor.execute("""
            INSERT INTO Teaches (userID, courseCode)
            VALUES (%s, %s)
        """, (lecturer_id, normalized_course_code))
        conn.commit()

        return jsonify({
            "message": "Lecturer assigned successfully",
            "courseCode": normalized_course_code,
            "lecturerID": lecturer_id
        }), 200
    except ValueError as err:
        conn.rollback()
        return jsonify({"error": str(err)}), 400
    except mysql.connector.Error as err:
        conn.rollback()
        if err.errno == DUPLICATE_ENTRY_ERRNO:
            return jsonify({"error": "Course already has an assigned lecturer"}), 409
        return jsonify({"error": str(err)}), 400
    finally:
        cursor.close()
        conn.close()


# GET /students/{userID}/courses - Basic Auth admin or target student reads courses.
@app.route("/students/<int:userID>/courses", methods=["GET"])
def student_courses(userID):
    user, auth_error = require_basic_auth()
    if auth_error:
        return auth_error
    if not can_read_student_resource(user, userID):
        return jsonify({"error": "User cannot read this student's courses"}), 403

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT c.courseCode, c.courseName, c.department
        FROM Course c
        JOIN CourseMember cm ON c.courseCode = cm.courseCode
        WHERE cm.userID = %s AND cm.memberRole = 'student'
    """, (userID,))
    courses = cursor.fetchall()
    cursor.close()
    conn.close()

    if courses:
        return jsonify(courses), 200
    return jsonify({"error": "No courses found for student"}), 404
    

# GET /lecturers/{userID}/courses - Basic Auth admin or target lecturer reads courses.
@app.route("/lecturers/<int:userID>/courses", methods=["GET"])
def lecturer_courses(userID):
    user, auth_error = require_basic_auth()
    if auth_error:
        return auth_error
    if not can_read_lecturer_resource(user, userID):
        return jsonify({"error": "User cannot read this lecturer's courses"}), 403

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT c.courseCode, c.courseName, c.department
        FROM Course c
        JOIN CourseMember cm ON c.courseCode = cm.courseCode
        WHERE cm.userID = %s AND cm.memberRole = 'lecturer'
    """, (userID,))
    courses = cursor.fetchall()
    cursor.close()
    conn.close()

    if courses:
        return jsonify(courses), 200
    return jsonify({"error": "No courses found for lecturer"}), 404


# GET /courses/{courseCode}/members - Basic Auth course viewer reads the roster.
@app.route('/courses/<courseCode>/members', methods=['GET']) 
def get_members(courseCode):
    user, auth_error = require_basic_auth()
    if auth_error:
        return auth_error

    try:
        course_code = clean_course_code(courseCode)
    except ValueError as err:
        return jsonify({"error": str(err)}), 400

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        if not course_exists(cursor, course_code):
            return jsonify({"error": "Course not found"}), 404
        if not can_view_course(cursor, user, course_code):
            return jsonify({"error": "User cannot view this course"}), 403

        cursor.execute("""
            SELECT
                u.userID,
                u.fname,
                u.lname,
                u.email,
                u.accessLvl,
                cm.memberRole,
                cm.courseCode
            FROM CourseMember cm
            JOIN UserAccount u ON cm.userID = u.userID
            WHERE cm.courseCode = %s
            ORDER BY
                CASE cm.memberRole
                    WHEN 'lecturer' THEN 1
                    WHEN 'student' THEN 2
                    ELSE 3
                END,
                u.lname ASC,
                u.fname ASC,
                u.userID ASC
        """, (course_code,))
        return jsonify(cursor.fetchall()), 200
    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 400
    finally:
        cursor.close()
        conn.close()


# GET /students/{userID}/grades - Basic Auth admin or target student reads course grades.
@app.route('/students/<userID>/grades', methods=['GET']) 
def get_student_grades(userID):
    user, auth_error = require_basic_auth()
    if auth_error:
        return auth_error

    try:
        user_id = parse_required_int(userID, "userID")
    except ValueError as err:
        return jsonify({"error": str(err)}), 400

    if not can_read_student_resource(user, user_id):
        return jsonify({"error": "User cannot read this student's grades"}), 403

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True) 

    cursor.execute("""SELECT grade, courseCode 
                        FROM Enrol
                        WHERE userID = %s;""",(user_id,))
    
    grades = cursor.fetchall() 
    cursor.close() 
    conn.close()

    return jsonify(grades)


# GET /students/{userID}/{courseCode}/grades - Basic Auth admin or target student reads one course grade.
@app.route('/students/<userID>/<courseCode>/grades', methods=['GET'])
def get_student_course_grades(userID, courseCode):
    user, auth_error = require_basic_auth()
    if auth_error:
        return auth_error

    try:
        user_id = parse_required_int(userID, "userID")
        course_code = clean_course_code(courseCode)
    except ValueError as err:
        return jsonify({"error": str(err)}), 400

    if not can_read_student_resource(user, user_id):
        return jsonify({"error": "User cannot read this student's grades"}), 403

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if not course_exists(cursor, course_code):
        cursor.close()
        conn.close()
        return jsonify({"error": "Course not found"}), 404

    cursor.execute("""
        SELECT grade
        FROM Enrol
        WHERE userID = %s AND courseCode = %s
    """, (user_id, course_code))

    grades = cursor.fetchall()
    cursor.close()
    conn.close()

    return jsonify(grades)


# POST /courses/{courseCode}/enrollments - Basic Auth admin enrolls a target student.
@app.route("/courses/<string:courseCode>/enrollments", methods=["POST"])
def enroll_student(courseCode):
    user, auth_error = require_basic_auth()
    if auth_error:
        return auth_error
    admin_error = require_admin_user(user)
    if admin_error:
        return admin_error

    data = request.get_json(silent=True) or {}

    try:
        course_code = clean_course_code(courseCode)
        user_id = parse_required_int(data.get("userID"), "userID")
        grade = parse_optional_grade(data.get("grade"))
    except ValueError as err:
        return jsonify({"error": str(err)}), 400

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        if not course_exists(cursor, course_code):
            return jsonify({"error": "Course not found"}), 404
        if not validate_student(cursor, user_id):
            return jsonify({"error": "userID must belong to a student user"}), 400
        if enrollment_exists(cursor, user_id, course_code):
            return jsonify({"error": "Student is already enrolled in this course"}), 409

        cursor.execute("""
            INSERT INTO Enrol (userID, courseCode, grade)
            VALUES (%s, %s, %s)
        """, (user_id, course_code, grade))
        conn.commit()
    except mysql.connector.Error as err:
        conn.rollback()
        if err.errno == DUPLICATE_ENTRY_ERRNO:
            return jsonify({"error": "Student is already enrolled in this course"}), 409
        return jsonify({"error": str(err)}), 400
    finally:
        cursor.close()
        conn.close()

    return jsonify({
        "message": "Enrollment successful",
        "userID": user_id,
        "courseCode": course_code,
        "grade": grade
    }), 201


# ---------------------------------------------------------------------------
# Course content routes
# ---------------------------------------------------------------------------

# GET /courses/{courseCode}/sections - Basic Auth course viewer reads content sections.
@app.route('/courses/<courseCode>/sections', methods=['GET'])
def get_course_sections(courseCode):
    user, auth_error = require_basic_auth()
    if auth_error:
        return auth_error

    try:
        course_code = clean_course_code(courseCode)
    except ValueError as err:
        return jsonify({"error": str(err)}), 400

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        if not course_exists(cursor, course_code):
            return jsonify({"error": "Course not found"}), 404
        if not can_view_course(cursor, user, course_code):
            return jsonify({"error": "User cannot view this course"}), 403

        cursor.execute("""
            SELECT secID, secName, courseCode
            FROM CourseSection
            WHERE courseCode = %s
            ORDER BY secID ASC
        """, (course_code,))
        return jsonify(cursor.fetchall()), 200
    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 400
    finally:
        cursor.close()
        conn.close()


# POST /courses/{courseCode}/sections - Basic Auth admin or assigned lecturer creates a section.
@app.route('/courses/<courseCode>/sections', methods=['POST'])
def create_course_section(courseCode):
    user, auth_error = require_basic_auth()
    if auth_error:
        return auth_error

    data = request.get_json(silent=True) or {}

    try:
        course_code = clean_course_code(courseCode)
        sec_name = clean_required_text(data.get("secName"), "secName", 50)
    except ValueError as err:
        return jsonify({"error": str(err)}), 400

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        if not course_exists(cursor, course_code):
            return jsonify({"error": "Course not found"}), 404
        if not can_manage_course(cursor, user, course_code):
            return jsonify({"error": "User cannot manage this course"}), 403

        cursor.execute("""
            INSERT INTO CourseSection (secName, courseCode)
            VALUES (%s, %s)
        """, (sec_name, course_code))
        conn.commit()
        sec_id = cursor.lastrowid

        return jsonify({
            "message": "Section created successfully",
            "section": {
                "secID": sec_id,
                "secName": sec_name,
                "courseCode": course_code
            }
        }), 201
    except mysql.connector.Error as err:
        conn.rollback()
        return jsonify({"error": str(err)}), 400
    finally:
        cursor.close()
        conn.close()


# GET /courses/{courseCode}/content - Basic Auth course viewer reads sections and items.
@app.route('/courses/<courseCode>/content', methods=['GET'])
def get_course_content(courseCode):
    user, auth_error = require_basic_auth()
    if auth_error:
        return auth_error

    try:
        course_code = clean_course_code(courseCode)
    except ValueError as err:
        return jsonify({"error": str(err)}), 400

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        if not course_exists(cursor, course_code):
            return jsonify({"error": "Course not found"}), 404
        if not can_view_course(cursor, user, course_code):
            return jsonify({"error": "User cannot view this course"}), 403

        cursor.execute("""
            SELECT
                cs.secID,
                cs.secName,
                si.secItemID,
                si.title,
                si.secBody,
                si.secContent,
                si.itemtype,
                si.dueDate
            FROM CourseSection cs
            LEFT JOIN SectionItems si ON cs.secID = si.secID
            WHERE cs.courseCode = %s
            ORDER BY cs.secID ASC, si.secItemID ASC
        """, (course_code,))

        sections = []
        sections_by_id = {}
        for row in cursor.fetchall():
            sec_id = row["secID"]
            if sec_id not in sections_by_id:
                section = {
                    "secID": sec_id,
                    "secName": row["secName"],
                    "items": []
                }
                sections_by_id[sec_id] = section
                sections.append(section)

            if row["secItemID"] is not None:
                due_date = row["dueDate"]
                if hasattr(due_date, "isoformat"):
                    due_date = due_date.isoformat()
                sections_by_id[sec_id]["items"].append({
                    "secItemID": row["secItemID"],
                    "title": row["title"],
                    "secBody": row["secBody"],
                    "secContent": row["secContent"],
                    "itemtype": row["itemtype"],
                    "dueDate": due_date
                })

        return jsonify(sections), 200
    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 400
    finally:
        cursor.close()
        conn.close()


# POST /sections/{secID}/items - Basic Auth admin or assigned lecturer adds course content.
@app.route('/sections/<secID>/items', methods=['POST'])
def create_section_item(secID):
    user, auth_error = require_basic_auth()
    if auth_error:
        return auth_error

    data = request.get_json(silent=True) or {}

    try:
        sec_id = parse_required_int(secID, "secID")
        title = clean_required_text(data.get("title"), "title", 50)
        sec_body = clean_optional_text(data.get("secBody"), "secBody", 500)
        sec_content = clean_optional_text(data.get("secContent"), "secContent", 1000)
        itemtype = clean_item_type(data.get("itemtype"))
        due_date = parse_item_due_date(itemtype, data.get("dueDate"))
    except ValueError as err:
        return jsonify({"error": str(err)}), 400

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        section = get_section_course(cursor, sec_id)
        if not section:
            return jsonify({"error": "Section not found"}), 404
        if not can_manage_course(cursor, user, section["courseCode"]):
            return jsonify({"error": "User cannot manage this course"}), 403

        cursor.execute("""
            INSERT INTO SectionItems (secID, title, secBody, secContent, itemtype, dueDate)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (sec_id, title, sec_body, sec_content, itemtype, due_date))
        conn.commit()
        sec_item_id = cursor.lastrowid

        return jsonify({
            "message": "Section item created successfully",
            "item": {
                "secItemID": sec_item_id,
                "secID": sec_id,
                "courseCode": section["courseCode"],
                "title": title,
                "secBody": sec_body,
                "secContent": sec_content,
                "itemtype": itemtype,
                "dueDate": due_date
            }
        }), 201
    except mysql.connector.Error as err:
        conn.rollback()
        return jsonify({"error": str(err)}), 400
    finally:
        cursor.close()
        conn.close()

# ---------------------------------------------------------------------------
# Assignment submission and grading routes
# ---------------------------------------------------------------------------

# POST /assignments/{secItemID}/submissions - Basic Auth enrolled student submits assignment work.
@app.route('/assignments/<secItemID>/submissions', methods=['POST'])
def submit_submission(secItemID):
    user, auth_error = require_basic_auth()
    if auth_error:
        return auth_error
    student_error = require_student_user(user)
    if student_error:
        return student_error

    data = request.get_json(silent=True) or {}

    try:
        sec_item_id = parse_required_int(secItemID, "secItemID")
        sub_text = clean_optional_string(data.get("subText"), "subText", 200)
        sub_content = data.get("subContent")

        if sub_content is not None:
            if not isinstance(sub_content, str):
                return jsonify({"error": "subContent must be text or null"}), 400
            sub_content = sub_content.strip() or None

        if sub_text is None and sub_content is None:
            return jsonify({"error": "subText or subContent is required"}), 400
    except ValueError as err:
        return jsonify({"error": str(err)}), 400

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        section_item = get_section_item_submission_context(cursor, sec_item_id)
        if not section_item:
            return jsonify({"error": "Section item not found"}), 404
        if section_item["itemtype"] != "assignment":
            return jsonify({"error": "Submissions are only allowed for assignment section items"}), 400
        user_id = user["userID"]
        if not enrollment_exists(cursor, user_id, section_item["courseCode"]):
            return jsonify({"error": "Student is not enrolled in this course"}), 403

        cursor.execute("""
            INSERT INTO Submission (userID, secItemID, subText, subContent, submDate, grade)
            VALUES (%s, %s, %s, %s, NOW(), NULL)
        """, (user_id, sec_item_id, sub_text, sub_content))

        conn.commit()
        inserted_id = cursor.lastrowid

        return jsonify({
            "message": "Submission created",
            "subID": inserted_id,
            "userID": user_id,
            "secItemID": sec_item_id
        }), 201
    except mysql.connector.Error as err:
        conn.rollback()
        return jsonify({"error": str(err)}), 400
    finally:
        cursor.close()
        conn.close()


# GET /assignments/{secItemID}/submissions - Basic Auth course manager reads submissions.
@app.route('/assignments/<secItemID>/submissions', methods=['GET'])
def get_assignment_submissions(secItemID):
    user, auth_error = require_basic_auth()
    if auth_error:
        return auth_error

    try:
        sec_item_id = parse_required_int(secItemID, "secItemID")
    except ValueError as err:
        return jsonify({"error": str(err)}), 400

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        section_item = get_section_item_submission_context(cursor, sec_item_id)
        if not section_item:
            return jsonify({"error": "Section item not found"}), 404
        if section_item["itemtype"] != "assignment":
            return jsonify({"error": "Submissions are only available for assignment section items"}), 400
        if not can_manage_course(cursor, user, section_item["courseCode"]):
            return jsonify({"error": "User cannot view submissions for this assignment"}), 403

        cursor.execute("""
            SELECT
                s.subID,
                s.userID,
                ua.fname,
                ua.lname,
                s.subText,
                s.subContent,
                s.submDate,
                s.grade
            FROM Submission s
            JOIN UserAccount ua ON s.userID = ua.userID
            WHERE s.secItemID = %s
            ORDER BY s.submDate DESC, s.subID DESC
        """, (sec_item_id,))

        submissions = []
        for row in cursor.fetchall():
            subm_date = row["submDate"]
            if hasattr(subm_date, "isoformat"):
                subm_date = subm_date.isoformat()
            row["submDate"] = subm_date
            submissions.append(row)

        return jsonify(submissions), 200
    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 400
    finally:
        cursor.close()
        conn.close()


# PUT /submissions/{subID}/grade - Basic Auth admin or assigned lecturer grades work.
@app.route('/submissions/<int:subID>/grade', methods=['PUT'])
def grade_assignment(subID):
    user, auth_error = require_basic_auth()
    if auth_error:
        return auth_error

    data = request.get_json(silent=True) or {}

    try:
        grade = parse_required_grade(data.get("grade"))
    except ValueError as err:
        return jsonify({"error": str(err)}), 400

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        submission_course = get_submission_course(cursor, subID)
        if not submission_course:
            return jsonify({"error": "Submission not found"}), 404
        if not can_manage_course(cursor, user, submission_course["courseCode"]):
            return jsonify({"error": "User cannot grade this submission"}), 403

        cursor.execute("""
            UPDATE Submission
            SET grade = %s
            WHERE subID = %s
        """, (grade, subID))

        cursor.execute("""
            SELECT subID, userID, secItemID, subText, submDate, grade
            FROM Submission
            WHERE subID = %s
        """, (subID,))
        graded_assignment = cursor.fetchone()
        course_grade = recalculate_enrollment_grade(
            cursor,
            submission_course["userID"],
            submission_course["courseCode"]
        )
        conn.commit()

        return jsonify({
            "message": "Submission graded successfully",
            "submission": graded_assignment,
            "courseGrade": course_grade
        }), 200
    except mysql.connector.Error as err:
        conn.rollback()
        return jsonify({"error": str(err)}), 400
    finally:
        cursor.close()
        conn.close()


# ---------------------------------------------------------------------------
# Forum and discussion routes
# ---------------------------------------------------------------------------

# GET /courses/{courseCode}/forums - Basic Auth course viewer reads course forums.
@app.route('/courses/<courseCode>/forums')
def get_course_forums(courseCode):
    user, auth_error = require_basic_auth()
    if auth_error:
        return auth_error

    try:
        course_code = clean_course_code(courseCode)
    except ValueError as err:
        return jsonify({"error": str(err)}), 400

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        if not course_exists(cursor, course_code):
            return jsonify({"error": "Course not found"}), 404
        if not can_view_course(cursor, user, course_code):
            return jsonify({"error": "User cannot view this course"}), 403

        cursor.execute("""
            SELECT f.dfID, f.dfname, f.courseCode
            FROM DiscussionForum f
            WHERE f.courseCode = %s
            ORDER BY f.dfID ASC
        """, (course_code,))
        return jsonify(cursor.fetchall()), 200
    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 400
    finally:
        cursor.close()
        conn.close()


# POST /courses/{courseCode}/forums - Basic Auth admin or assigned lecturer creates a forum.
@app.route('/courses/<courseCode>/forums', methods=['POST'])
def create_course_forum(courseCode):
    user, auth_error = require_basic_auth()
    if auth_error:
        return auth_error

    data = request.get_json(silent=True) or {}

    try:
        course_code = clean_course_code(courseCode)
        dfname = clean_required_text(data.get("dfname"), "dfname", 50)
    except ValueError as err:
        return jsonify({"error": str(err)}), 400

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        if not course_exists(cursor, course_code):
            return jsonify({"error": "Course not found"}), 404
        if not can_manage_course(cursor, user, course_code):
            return jsonify({"error": "User cannot manage this course"}), 403

        cursor.execute("""
            INSERT INTO DiscussionForum (dfname, courseCode)
            VALUES (%s, %s)
        """, (dfname, course_code))
        conn.commit()
        df_id = cursor.lastrowid

        return jsonify({
            "message": "Forum created successfully",
            "dfID": df_id,
            "dfname": dfname,
            "courseCode": course_code
        }), 201
    except mysql.connector.Error as err:
        conn.rollback()
        return jsonify({"error": str(err)}), 400
    finally:
        cursor.close()
        conn.close()


# GET /forums/{dfID}/threads - Basic Auth course viewer reads top-level threads.
@app.route('/forums/<dfID>/threads', methods=['GET'])
def get_forum_threads(dfID):
    user, auth_error = require_basic_auth()
    if auth_error:
        return auth_error

    try:
        df_id = parse_required_int(dfID, "dfID")
    except ValueError as err:
        return jsonify({"error": str(err)}), 400

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        forum = get_forum_course(cursor, df_id)
        if not forum:
            return jsonify({"error": "Forum not found"}), 404
        if not can_view_course(cursor, user, forum["courseCode"]):
            return jsonify({"error": "User cannot view this course"}), 403

        cursor.execute("""
            SELECT
                dt.dtID,
                dt.dfID,
                df.courseCode,
                dt.parentpostID,
                dt.userID,
                ua.fname,
                ua.lname,
                dt.topic,
                dt.threadbody,
                dt.date_created,
                COUNT(reply.dtID) AS replyCount
            FROM DiscussionThread dt
            JOIN DiscussionForum df ON dt.dfID = df.dfID
            JOIN UserAccount ua ON dt.userID = ua.userID
            LEFT JOIN DiscussionThread reply
                ON reply.parentpostID = dt.dtID
                AND reply.dfID = dt.dfID
            WHERE dt.dfID = %s AND dt.parentpostID IS NULL
            GROUP BY
                dt.dtID,
                dt.dfID,
                df.courseCode,
                dt.parentpostID,
                dt.userID,
                ua.fname,
                ua.lname,
                dt.topic,
                dt.threadbody,
                dt.date_created
            ORDER BY dt.date_created DESC, dt.dtID DESC
        """, (df_id,))
        threads = []
        for row in cursor.fetchall():
            thread = serialize_discussion_post(row)
            thread.pop("replies")
            thread.pop("parentpostID")
            thread["replyCount"] = row["replyCount"]
            threads.append(thread)
        return jsonify(threads), 200
    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 400
    finally:
        cursor.close()
        conn.close()


# POST /forums/{dfID}/threads - Basic Auth admin or course member starts a thread.
@app.route('/forums/<dfID>/threads', methods=['POST'])
def create_thread(dfID):
    user, auth_error = require_basic_auth()
    if auth_error:
        return auth_error

    data = request.get_json(silent=True) or {}

    try:
        df_id = parse_required_int(dfID, "dfID")
        thread_body = clean_required_text(data.get("threadbody"), "threadbody", 500)
        topic = clean_optional_text(data.get("topic"), "topic", 20)
    except ValueError as err:
        return jsonify({"error": str(err)}), 400

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        forum = get_forum_course(cursor, df_id)
        if not forum:
            return jsonify({"error": "Forum not found"}), 404
        if not can_post_in_course(cursor, user, forum["courseCode"]):
            return jsonify({"error": "User is not a member of this course"}), 403

        cursor.execute("""
            INSERT INTO DiscussionThread
            (dfID, parentpostID, userID, threadbody, topic, date_created)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            df_id,
            None,
            user["userID"],
            thread_body,
            topic,
            date.today()
        ))

        conn.commit()
        inserted_id = cursor.lastrowid

        return jsonify({
            "message": "Thread created successfully",
            "dtID": inserted_id,
            "dfID": df_id,
            "userID": user["userID"],
            "courseCode": forum["courseCode"]
        }), 201
    except mysql.connector.Error as err:
        conn.rollback()
        return jsonify({"error": str(err)}), 400
    finally:
        cursor.close()
        conn.close()


# GET /threads/{dtID} - Basic Auth course viewer reads one thread with nested replies.
@app.route('/threads/<dtID>', methods=['GET'])
def get_thread(dtID):
    user, auth_error = require_basic_auth()
    if auth_error:
        return auth_error

    try:
        thread_id = parse_required_int(dtID, "dtID")
    except ValueError as err:
        return jsonify({"error": str(err)}), 400

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        root_post = get_discussion_post(cursor, thread_id)
        if not root_post:
            return jsonify({"error": "Thread not found"}), 404
        if root_post["parentpostID"] is not None:
            return jsonify({"error": "dtID must belong to a top-level thread"}), 400
        if not can_view_course(cursor, user, root_post["courseCode"]):
            return jsonify({"error": "User cannot view this course"}), 403

        cursor.execute("""
            SELECT
                dt.dtID,
                dt.dfID,
                df.courseCode,
                dt.parentpostID,
                dt.userID,
                ua.fname,
                ua.lname,
                dt.topic,
                dt.threadbody,
                dt.date_created
            FROM DiscussionThread dt
            JOIN DiscussionForum df ON dt.dfID = df.dfID
            JOIN UserAccount ua ON dt.userID = ua.userID
            WHERE dt.dfID = %s
            ORDER BY dt.date_created ASC, dt.dtID ASC
        """, (root_post["dfID"],))

        thread = build_reply_tree(cursor.fetchall(), thread_id)
        return jsonify(thread), 200
    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 400
    finally:
        cursor.close()
        conn.close()


# POST /threads/{dtID}/replies - Basic Auth admin or course member replies to a post.
@app.route('/threads/<dtID>/replies', methods=['POST'])
def reply_to_thread(dtID):
    user, auth_error = require_basic_auth()
    if auth_error:
        return auth_error

    data = request.get_json(silent=True) or {}

    try:
        parent_post_id = parse_required_int(dtID, "dtID")
        thread_body = clean_required_text(data.get("threadbody"), "threadbody", 500)
        topic = clean_optional_text(data.get("topic"), "topic", 20)
    except ValueError as err:
        return jsonify({"error": str(err)}), 400

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        parent = get_thread_context(cursor, parent_post_id)
        if not parent:
            return jsonify({"error": "Parent thread not found"}), 404
        if not can_post_in_course(cursor, user, parent["courseCode"]):
            return jsonify({"error": "User is not a member of this course"}), 403

        cursor.execute("""
            INSERT INTO DiscussionThread
            (dfID, parentpostID, userID, threadbody, topic, date_created)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            parent["dfID"],
            parent_post_id,
            user["userID"],
            thread_body,
            topic,
            date.today()
        ))

        conn.commit()
        inserted_id = cursor.lastrowid

        return jsonify({
            "message": "Reply created successfully",
            "dtID": inserted_id,
            "parentpostID": parent_post_id,
            "dfID": parent["dfID"],
            "userID": user["userID"],
            "courseCode": parent["courseCode"]
        }), 201
    except mysql.connector.Error as err:
        conn.rollback()
        return jsonify({"error": str(err)}), 400
    finally:
        cursor.close()
        conn.close()


# ---------------------------------------------------------------------------
# Calendar routes
# ---------------------------------------------------------------------------

# GET /courses/{courseCode}/calendar-events - Basic Auth course viewer reads course events.
@app.route('/courses/<courseCode>/calendar-events', methods=['GET'])
def course_events(courseCode):
    user, auth_error = require_basic_auth()
    if auth_error:
        return auth_error

    try:
        course_code = clean_course_code(courseCode)
    except ValueError as err:
        return jsonify({"error": str(err)}), 400

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        if not course_exists(cursor, course_code):
            return jsonify({"error": "Course not found"}), 404
        if not can_view_course(cursor, user, course_code):
            return jsonify({"error": "User cannot view this course"}), 403

        cursor.execute("""
            SELECT courseCode, courseName, eventID, calendarID, eventDate, eventTitle, secItemID
            FROM course_calendar_events
            WHERE courseCode = %s
            ORDER BY eventDate ASC, eventID ASC
        """, (course_code,))
        return jsonify(cursor.fetchall()), 200
    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 400
    finally:
        cursor.close()
        conn.close()


# POST /courses/{courseCode}/calendar-events - Basic Auth admin or assigned lecturer creates an event.
@app.route('/courses/<courseCode>/calendar-events', methods=['POST'])
def create_calendar_event(courseCode):
    user, auth_error = require_basic_auth()
    if auth_error:
        return auth_error

    data = request.get_json(silent=True) or {}

    try:
        course_code = clean_course_code(courseCode)
        event_date = parse_required_date(data.get("eventDate"), "eventDate")
        event_title = clean_required_text(data.get("eventTitle"), "eventTitle", 50)
        sec_item_id = parse_optional_int(data.get("secItemID"), "secItemID")
    except ValueError as err:
        return jsonify({"error": str(err)}), 400

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        if not course_exists(cursor, course_code):
            return jsonify({"error": "Course not found"}), 404
        if not can_manage_course(cursor, user, course_code):
            return jsonify({"error": "User cannot manage this course"}), 403

        calendar = get_course_calendar(cursor, course_code)
        if not calendar:
            return jsonify({"error": "Course calendar not found"}), 404

        if sec_item_id is not None:
            section_item = get_section_item_submission_context(cursor, sec_item_id)
            if not section_item:
                return jsonify({"error": "Section item not found"}), 404
            if section_item["courseCode"] != course_code:
                return jsonify({"error": "secItemID must belong to this course"}), 400

        cursor.execute("""
            INSERT INTO CalendarEvents (calendarID, eventDate, eventTitle, secItemID)
            VALUES (%s, %s, %s, %s)
        """, (calendar["calendarID"], event_date, event_title, sec_item_id))
        conn.commit()
        event_id = cursor.lastrowid

        return jsonify({
            "message": "Calendar event created successfully",
            "eventID": event_id,
            "courseCode": course_code,
            "calendarID": calendar["calendarID"],
            "eventDate": event_date,
            "eventTitle": event_title,
            "secItemID": sec_item_id
        }), 201
    except mysql.connector.Error as err:
        conn.rollback()
        return jsonify({"error": str(err)}), 400
    finally:
        cursor.close()
        conn.close()


# GET /students/{userID}/calendar-events - Basic Auth admin or target student reads calendar events.
@app.route('/students/<userID>/calendar-events', methods=['GET'])
def student_events(userID):
    user, auth_error = require_basic_auth()
    if auth_error:
        return auth_error

    try:
        user_id = parse_required_int(userID, "userID")
        event_date = parse_optional_date(request.args.get("date"))
    except ValueError as err:
        return jsonify({"error": str(err)}), 400

    if not can_read_student_resource(user, user_id):
        return jsonify({"error": "User cannot read this student's calendar events"}), 403

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        if event_date:
            cursor.execute("""
                SELECT userID, courseCode, courseName, eventID, calendarID, eventDate, eventTitle, secItemID
                FROM student_calendar_events
                WHERE userID = %s AND eventDate = %s
                ORDER BY courseCode ASC, eventDate ASC, eventID ASC
            """, (user_id, event_date))
        else:
            cursor.execute("""
                SELECT userID, courseCode, courseName, eventID, calendarID, eventDate, eventTitle, secItemID
                FROM student_calendar_events
                WHERE userID = %s
                ORDER BY courseCode ASC, eventDate ASC, eventID ASC
            """, (user_id,))
        return jsonify(cursor.fetchall()), 200
    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 400
    finally:
        cursor.close()
        conn.close()


# ---------------------------------------------------------------------------
# Report routes
# ---------------------------------------------------------------------------

# GET /reports/courses-50 - public report for courses with 50 or more students.
@app.route('/reports/courses-50', methods=['GET']) 
def top_fifty_courses():
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True) 
    cursor.execute("SELECT courseCode, student_count FROM course_50_plus")
    top_fifty = cursor.fetchall() 
    cursor.close() 
    conn.close()

    return jsonify(top_fifty)


# GET /reports/students-5plus - public report for students taking 5 or more courses.
@app.route("/reports/students-5plus", methods=["GET"])
def students_5plus():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM students_5_plus_courses")
    students = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(students), 200



# GET /reports/lecturers-3 - public report for lecturers teaching 3 or more courses.
@app.route('/reports/lecturers-3', methods=['GET']) 
def top_3_lecturers():

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True) 
    cursor.execute("SELECT fname, lname, num_courses FROM lecturers_3_plus")
    top_3 = cursor.fetchall() 
    cursor.close() 
    conn.close()

    return jsonify(top_3)


# GET /reports/most-enrolled - public report for the 10 most enrolled courses.
@app.route("/reports/most-enrolled", methods=["GET"])
def most_enrolled_course():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM ten_most_enrolled")
    course = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(course), 200


# GET /reports/top-students-by-average - public report for top course-grade averages.
@app.route("/reports/top-students-by-average", methods=["GET"])
def top_students_by_average():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM top_ten_students")
    students = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(students), 200


if __name__ =='__main__':
    app.run(debug=True)
