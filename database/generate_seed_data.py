"""
Deterministic seed-data generator for the VLE database.

The generator targets the schema in database/schema.sql and writes:
  - database/generated_seed.sql
  - docs/demo_credentials.txt

It validates the generated dataset before writing SQL so coursework data
constraints fail fast instead of producing a broken seed file.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from datetime import date
import hashlib
import os
import random
import re
from typing import Any

from faker import Faker


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(BASE_DIR)
OUTPUT_FILE = os.path.join(BASE_DIR, "generated_seed.sql")
DEMO_CREDENTIALS_FILE = os.path.join(REPO_ROOT, "docs", "demo_credentials.txt")

RANDOM_SEED = 42
BATCH_SIZE = 500

NUM_STUDENTS = 100_000
NUM_LECTURERS = 200
NUM_ADMINS = 10
NUM_COURSES = 300

MIN_STUDENT_COURSES = 3
MAX_STUDENT_COURSES = 6
MIN_COURSE_STUDENTS = 10
MIN_LECTURER_COURSES = 1
MAX_LECTURER_COURSES = 5
TARGET_LECTURERS_WITH_3_PLUS = 40

STUDENT_START_ID = 620_000_000
LECTURER_START_ID = 200_000_000
ADMIN_START_ID = 111_000_000

COURSE_CODE_RE = re.compile(r"^[A-Z0-9]{8}$")
ITEM_TYPES = ("assignment", "link", "file", "slide")

fake = Faker()


# ---------------------------------------------------------------------------
# Static course catalog inputs
# ---------------------------------------------------------------------------

DEPARTMENTS = [
    "Computer Science", "Mathematics", "Physics", "Chemistry", "Biology",
    "Engineering", "Economics", "Management", "Law", "Medicine",
    "Psychology", "Sociology", "History", "Literature", "Philosophy",
    "Agriculture", "Education", "Nursing", "Architecture", "Accounting",
]

COURSE_PREFIXES = {
    "Computer Science": "COMP", "Mathematics": "MATH", "Physics": "PHYS",
    "Chemistry": "CHEM", "Biology": "BIOL", "Engineering": "ENGR",
    "Economics": "ECON", "Management": "MGMT", "Law": "LAW0",
    "Medicine": "MEDI", "Psychology": "PSYC", "Sociology": "SOCI",
    "History": "HIST", "Literature": "LITE", "Philosophy": "PHIL",
    "Agriculture": "AGRI", "Education": "EDUC", "Nursing": "NURS",
    "Architecture": "ARCH", "Accounting": "ACCT",
}

COURSE_TOPICS = {
    "Computer Science": [
        "Intro to Programming", "Data Structures", "Algorithms", "Operating Systems",
        "Database Systems", "Computer Networks", "Software Engineering",
        "Artificial Intelligence", "Machine Learning", "Cybersecurity",
        "Web Development", "Mobile Computing", "Cloud Computing",
        "Computer Graphics", "Theory of Computation",
    ],
    "Mathematics": [
        "Calculus I", "Calculus II", "Linear Algebra", "Discrete Mathematics",
        "Probability and Statistics", "Real Analysis", "Abstract Algebra",
        "Numerical Methods", "Differential Equations", "Topology", "Number Theory",
        "Graph Theory", "Complex Analysis", "Mathematical Modelling",
        "Operations Research",
    ],
    "Physics": [
        "Mechanics", "Electromagnetism", "Thermodynamics", "Quantum Physics",
        "Optics", "Nuclear Physics", "Astrophysics", "Condensed Matter",
        "Fluid Dynamics", "Acoustics", "Relativity", "Plasma Physics",
        "Computational Physics", "Experimental Methods", "Particle Physics",
    ],
    "Chemistry": [
        "General Chemistry", "Organic Chemistry", "Inorganic Chemistry",
        "Physical Chemistry", "Analytical Chemistry", "Biochemistry",
        "Polymer Chemistry", "Environmental Chemistry", "Spectroscopy",
        "Electrochemistry", "Medicinal Chemistry", "Computational Chemistry",
        "Industrial Chemistry", "Nanochemistry", "Food Chemistry",
    ],
    "Biology": [
        "Cell Biology", "Genetics", "Ecology", "Evolution", "Microbiology",
        "Zoology", "Botany", "Physiology", "Immunology", "Molecular Biology",
        "Neuroscience", "Marine Biology", "Conservation Biology",
        "Developmental Biology", "Parasitology",
    ],
    "Engineering": [
        "Engineering Mathematics", "Statics", "Dynamics", "Materials Science",
        "Thermodynamics", "Fluid Mechanics", "Circuit Analysis", "Control Systems",
        "Signal Processing", "Structural Analysis", "Environmental Engineering",
        "Geotechnical Engineering", "Manufacturing Processes", "Project Management",
        "Engineering Ethics",
    ],
    "Economics": [
        "Microeconomics", "Macroeconomics", "Development Economics",
        "International Economics", "Public Finance", "Econometrics",
        "Labour Economics", "Environmental Economics", "Health Economics",
        "Monetary Economics", "Industrial Organisation", "Behavioural Economics",
        "Game Theory", "Economic History", "Financial Economics",
    ],
    "Management": [
        "Principles of Management", "Organisational Behaviour",
        "Marketing Management", "Human Resource Management", "Strategic Management",
        "Operations Management", "Entrepreneurship", "Business Ethics",
        "Innovation Management", "Supply Chain Management", "Project Management Adv",
        "Change Management", "Leadership", "Corporate Governance", "Risk Management",
    ],
    "Law": [
        "Constitutional Law", "Contract Law", "Criminal Law", "Tort Law",
        "Property Law", "Administrative Law", "International Law", "Company Law",
        "Human Rights Law", "Family Law", "Labour Law", "Intellectual Property",
        "Environmental Law", "Tax Law", "Procedure and Evidence",
    ],
    "Medicine": [
        "Anatomy", "Physiology", "Biochemistry", "Pharmacology", "Pathology",
        "Microbiology", "Community Health", "Clinical Medicine", "Surgery",
        "Paediatrics", "Obstetrics", "Psychiatry", "Radiology", "Ophthalmology",
        "Forensic Medicine",
    ],
    "Psychology": [
        "Introduction to Psychology", "Cognitive Psychology", "Social Psychology",
        "Developmental Psychology", "Abnormal Psychology", "Personality Psychology",
        "Biopsychology", "Research Methods", "Clinical Psychology",
        "Health Psychology", "Forensic Psychology", "Educational Psychology",
        "Organisational Psychology", "Positive Psychology", "Neuropsychology",
    ],
    "Sociology": [
        "Introduction to Sociology", "Social Theory", "Research Methods",
        "Gender Studies", "Race and Ethnicity", "Urban Sociology", "Rural Sociology",
        "Criminology", "Social Policy", "Globalisation", "Cultural Sociology",
        "Medical Sociology", "Political Sociology", "Family Sociology",
        "Environmental Sociology",
    ],
    "History": [
        "Ancient History", "Medieval History", "Modern History", "Caribbean History",
        "African History", "World Wars", "Colonial History", "History of Science",
        "Social History", "Political History", "Economic History", "Historiography",
        "Latin American History", "Asian History", "History of Religion",
    ],
    "Literature": [
        "Introduction to Literature", "Poetry Analysis", "Prose Fiction",
        "Drama and Theatre", "Caribbean Literature", "African Literature",
        "Postcolonial Literature", "Literary Theory", "Creative Writing",
        "Comparative Literature", "Childrens Literature", "Film and Literature",
        "Womens Writing", "World Literature", "Language and Linguistics",
    ],
    "Philosophy": [
        "Introduction to Philosophy", "Logic", "Ethics", "Political Philosophy",
        "Metaphysics", "Epistemology", "Philosophy of Mind", "Philosophy of Science",
        "Aesthetics", "Philosophy of Language", "Eastern Philosophy", "Applied Ethics",
        "Philosophy of Religion", "Continental Philosophy", "Analytic Philosophy",
    ],
    "Agriculture": [
        "Crop Science", "Animal Science", "Soil Science", "Agricultural Economics",
        "Agronomy", "Horticulture", "Pest Management", "Agricultural Engineering",
        "Irrigation Management", "Food Science", "Post Harvest Technology",
        "Aquaculture", "Agroforestry", "Agricultural Extension",
        "Sustainable Agriculture",
    ],
    "Education": [
        "Philosophy of Education", "Curriculum Development", "Educational Psychology",
        "Assessment and Evaluation", "Special Education", "Early Childhood Education",
        "STEM Education", "ICT in Education", "Literacy Education",
        "Educational Leadership", "Comparative Education", "Adult Education",
        "Guidance and Counselling", "Sociology of Education", "Teaching Practice",
    ],
    "Nursing": [
        "Fundamentals of Nursing", "Anatomy for Nurses", "Medical Surgical Nursing",
        "Paediatric Nursing", "Maternal and Child Health", "Mental Health Nursing",
        "Community Nursing", "Pharmacology for Nurses", "Critical Care Nursing",
        "Nursing Research", "Nursing Ethics", "Geriatric Nursing", "Oncology Nursing",
        "Emergency Nursing", "Nursing Leadership",
    ],
    "Architecture": [
        "Architectural Design", "History of Architecture", "Building Construction",
        "Structural Systems", "Environmental Design", "Urban Planning",
        "Landscape Architecture", "Architectural Theory", "Digital Design",
        "Building Services", "Housing Design", "Heritage Conservation",
        "Interior Architecture", "Professional Practice", "Building Information Modelling",
    ],
    "Accounting": [
        "Financial Accounting", "Management Accounting", "Auditing", "Taxation",
        "Cost Accounting", "Financial Reporting", "Accounting Information Systems",
        "Corporate Finance", "Forensic Accounting", "Public Sector Accounting",
        "International Accounting", "Accounting Theory", "Business Law for Accountants",
        "Advanced Auditing", "Financial Analysis",
    ],
}


# ---------------------------------------------------------------------------
# Small formatting helpers
# ---------------------------------------------------------------------------

def student_id(index: int) -> int:
    """Return the deterministic student userID for a zero-based index."""
    return STUDENT_START_ID + index


def lecturer_id(index: int) -> int:
    """Return the deterministic lecturer userID for a zero-based index."""
    return LECTURER_START_ID + index


def admin_id(index: int) -> int:
    """Return the deterministic admin userID for a zero-based index."""
    return ADMIN_START_ID + index


def hash_pw(plain: str) -> str:
    """Return the full SHA-256 password hash stored in UserAccount."""
    return hashlib.sha256(plain.encode()).hexdigest()


def clean_text(value: Any, max_len: int) -> str:
    """Flatten generated text so SQL inserts stay one row per value."""
    return str(value).replace("\r", " ").replace("\n", " ")[:max_len]


def make_email(fname: str, lname: str, used_emails: set[str], suffix: str = "") -> str:
    """Create a unique synthetic VLE email address."""
    base = f"{fname.lower()}.{lname.lower()}{suffix}".replace("'", "")
    email = f"{base}@vle.uwi.edu"
    counter = 1
    while email in used_emails:
        email = f"{base}{counter}@vle.uwi.edu"
        counter += 1
    used_emails.add(email)
    return email


def sql_value(value: Any) -> str:
    """Convert a Python value into a MySQL literal for the seed file."""
    if value is None:
        return "NULL"
    if isinstance(value, bool):
        return "1" if value else "0"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, date):
        return f"'{value.isoformat()}'"
    text = str(value).replace("\\", "\\\\").replace("'", "''")
    return f"'{text}'"


def write_insert_batches(handle, table: str, columns: list[str], rows: list[tuple[Any, ...]]) -> None:
    """Write rows as batched INSERT statements to keep the SQL file loadable."""
    column_sql = ", ".join(columns)
    for start in range(0, len(rows), BATCH_SIZE):
        batch = rows[start : start + BATCH_SIZE]
        values = [
            "(" + ",".join(sql_value(value) for value in row) + ")"
            for row in batch
        ]
        handle.write(f"INSERT INTO {table} ({column_sql}) VALUES\n")
        handle.write(",\n".join(values))
        handle.write(";\n")


# ---------------------------------------------------------------------------
# Dataset generation phases
# ---------------------------------------------------------------------------

def generate_users() -> dict[str, Any]:
    """Generate students, lecturers, admins, hashes, and demo plaintext lookup."""
    print("Generating users...")
    used_emails: set[str] = set()
    users: list[tuple[Any, ...]] = []
    user_lookup: dict[int, dict[str, Any]] = {}

    def add_user(user_id: int, access_lvl: str, password: str, suffix: str = "") -> None:
        fname = clean_text(fake.first_name(), 50)
        lname = clean_text(fake.last_name(), 50)
        email = make_email(fname, lname, used_emails, suffix)
        users.append((user_id, fname, lname, email, access_lvl, hash_pw(password)))
        user_lookup[user_id] = {
            "userID": user_id,
            "fname": fname,
            "lname": lname,
            "email": email,
            "accessLvl": access_lvl,
            "password": password,
        }

    for index in range(NUM_STUDENTS):
        uid = student_id(index)
        add_user(uid, "student", f"Student@{uid}")
        if (index + 1) % 25_000 == 0:
            print(f"  {index + 1:,} students...")

    for index in range(NUM_LECTURERS):
        uid = lecturer_id(index)
        add_user(uid, "lecturer", f"Lecturer@{uid}", f"_lec{index}")

    for index in range(NUM_ADMINS):
        uid = admin_id(index)
        add_user(uid, "admin", f"Admin@{uid}", f"_adm{index}")

    return {
        "users": users,
        "user_lookup": user_lookup,
        "student_ids": [student_id(index) for index in range(NUM_STUDENTS)],
        "lecturer_ids": [lecturer_id(index) for index in range(NUM_LECTURERS)],
        "admin_ids": [admin_id(index) for index in range(NUM_ADMINS)],
    }


def generate_courses() -> dict[str, Any]:
    """Generate the fixed course catalog with valid 8-character course codes."""
    print("Generating courses...")
    courses: list[tuple[Any, ...]] = []
    counters = {department: 1 for department in DEPARTMENTS}

    for department in DEPARTMENTS:
        prefix = COURSE_PREFIXES[department]
        for topic in COURSE_TOPICS[department]:
            code = f"{prefix}{counters[department]:04d}"[:8]
            name = clean_text(f"{prefix} {topic}", 50)
            courses.append((code, name, department))
            counters[department] += 1

    if len(courses) != NUM_COURSES:
        raise ValueError(f"Expected {NUM_COURSES} courses, generated {len(courses)}")

    return {
        "courses": courses,
        "course_codes": [course[0] for course in courses],
    }


def assign_lecturers(lecturer_ids: list[int], course_codes: list[str]) -> dict[str, Any]:
    """Assign exactly one lecturer per course while keeping each lecturer at 1-5 courses."""
    print("Assigning lecturers to courses...")
    shuffled_lecturers = lecturer_ids[:]
    shuffled_courses = course_codes[:]
    random.shuffle(shuffled_lecturers)
    random.shuffle(shuffled_courses)

    lecturer_courses = {lecturer: [] for lecturer in lecturer_ids}
    course_lecturer: dict[str, int] = {}
    unassigned_courses = shuffled_courses[:]

    def assign(lecturer: int, course: str) -> None:
        lecturer_courses[lecturer].append(course)
        course_lecturer[course] = lecturer

    # First pass guarantees every lecturer teaches at least one course.
    for lecturer in shuffled_lecturers:
        assign(lecturer, unassigned_courses.pop())

    # Some lecturers intentionally teach 3+ courses so the lecturer report has data.
    heavy_count = min(TARGET_LECTURERS_WITH_3_PLUS, len(unassigned_courses) // 2)
    for lecturer in random.sample(shuffled_lecturers, heavy_count):
        while unassigned_courses and len(lecturer_courses[lecturer]) < 3:
            assign(lecturer, unassigned_courses.pop())

    for course in unassigned_courses:
        candidates = [
            lecturer for lecturer in lecturer_ids
            if len(lecturer_courses[lecturer]) < MAX_LECTURER_COURSES
        ]
        if not candidates:
            raise ValueError("No lecturer has capacity for remaining course assignment")
        lightest_load = min(len(lecturer_courses[lecturer]) for lecturer in candidates)
        lightest = [
            lecturer for lecturer in candidates
            if len(lecturer_courses[lecturer]) == lightest_load
        ]
        assign(random.choice(lightest), course)

    teaches = [
        (course_lecturer[course_code], course_code)
        for course_code in course_codes
    ]

    return {
        "teaches": teaches,
        "lecturer_courses": lecturer_courses,
        "course_lecturer": course_lecturer,
    }


def enroll_students(student_ids: list[int], course_codes: list[str]) -> dict[str, Any]:
    """Assign 3-6 courses per student and repair courses below the member minimum."""
    print("Enrolling students...")
    student_courses: dict[int, set[str]] = {}

    for index, sid in enumerate(student_ids):
        target_count = random.randint(MIN_STUDENT_COURSES, MAX_STUDENT_COURSES)
        student_courses[sid] = set(random.sample(course_codes, target_count))
        if (index + 1) % 25_000 == 0:
            print(f"  {index + 1:,} students enrolled...")

    course_students: dict[str, set[int]] = {course: set() for course in course_codes}
    for sid, courses in student_courses.items():
        for course in courses:
            course_students[course].add(sid)

    for course in course_codes:
        while len(course_students[course]) < MIN_COURSE_STUDENTS:
            candidates = [
                sid for sid in student_ids
                if course not in student_courses[sid]
                and len(student_courses[sid]) < MAX_STUDENT_COURSES
            ]
            if not candidates:
                raise ValueError(f"Cannot repair enrollment count for {course}")
            sid = random.choice(candidates)
            student_courses[sid].add(course)
            course_students[course].add(sid)

    enrol_pairs = sorted(
        (sid, course)
        for sid, courses in student_courses.items()
        for course in courses
    )

    print(f"  {len(enrol_pairs):,} enrollments prepared.")
    return {
        "student_courses": student_courses,
        "course_students": course_students,
        "enrol_pairs": enrol_pairs,
    }


def generate_forums_and_threads(
    course_codes: list[str],
    course_students: dict[str, set[int]],
    course_lecturer: dict[str, int],
) -> dict[str, Any]:
    """Generate two forums per course with top-level posts and simple replies."""
    print("Generating forums and threads...")
    forum_names = ["General Discussion", "Q and A"]
    thread_topics = ["Question", "Help", "Discussion", "Feedback", "Clarification", "Resources", "Review"]
    forums: list[tuple[Any, ...]] = []
    threads: list[tuple[Any, ...]] = []
    forum_id = 1
    thread_id = 1

    for course in course_codes:
        members = list(course_students[course]) + [course_lecturer[course]]
        for forum_name in forum_names:
            forums.append((forum_id, forum_name, course))
            root_ids: list[int] = []
            for _ in range(3):
                body = clean_text(fake.sentence(nb_words=random.randint(8, 25)), 500)
                topic = random.choice(thread_topics)
                created = fake.date_between(start_date="-2y", end_date="today")
                user_id = random.choice(members)
                threads.append((thread_id, forum_id, None, user_id, body, topic, created))
                root_ids.append(thread_id)
                thread_id += 1

            for root_id in root_ids:
                for _ in range(random.randint(1, 3)):
                    body = clean_text(fake.sentence(nb_words=random.randint(5, 15)), 500)
                    created = fake.date_between(start_date="-2y", end_date="today")
                    user_id = random.choice(members)
                    threads.append((thread_id, forum_id, root_id, user_id, body, None, created))
                    thread_id += 1
            forum_id += 1

    return {"forums": forums, "threads": threads}


def generate_sections_and_items(course_codes: list[str]) -> dict[str, Any]:
    """Generate content sections and assignment/link/file/slide metadata items."""
    print("Generating sections and section items...")
    section_names = [
        "Week 1 - Introduction", "Week 2 - Core Concepts", "Week 3 - Applications",
        "Week 4 - Advanced Topics", "Week 5 - Case Studies", "Week 6 - Group Work",
        "Midterm Review", "Week 8", "Week 9", "Week 10", "Week 11",
        "Final Review", "Assignments", "Resources", "Announcements",
    ]
    item_titles = [
        "Lecture Notes", "Assignment {}", "Reading Material", "Tutorial Slides",
        "Lab Sheet", "Problem Set {}", "Quiz {}", "Project Guidelines",
        "Reference Links", "Supplementary Reading",
    ]

    sections: list[tuple[Any, ...]] = []
    section_by_course: dict[str, list[int]] = {}
    section_course: dict[int, str] = {}
    section_items: list[tuple[Any, ...]] = []
    assignment_items_by_course: dict[str, list[int]] = {course: [] for course in course_codes}

    section_id = 1
    item_id = 1

    for course in course_codes:
        section_by_course[course] = []
        for name in random.sample(section_names, random.randint(5, 10)):
            sections.append((section_id, name, course))
            section_by_course[course].append(section_id)
            section_course[section_id] = course

            for item_index in range(random.randint(2, 5)):
                item_type = random.choice(ITEM_TYPES)
                title = clean_text(random.choice(item_titles).format(item_index + 1), 50)
                body = clean_text(fake.sentence(nb_words=15), 500)
                if item_type == "link":
                    content = f"https://resources.vle.local/{course.lower()}/item-{item_id}"
                elif item_type == "file":
                    content = f"files/{course.lower()}/resource-{item_id}.pdf"
                elif item_type == "slide":
                    content = f"slides/{course.lower()}/deck-{item_id}.pdf"
                else:
                    content = clean_text(fake.sentence(nb_words=12), 1000)
                due_date = fake.date_between(start_date="-1y", end_date="+6m") if item_type == "assignment" else None

                section_items.append((item_id, section_id, title, body, content, item_type, due_date))
                if item_type == "assignment":
                    assignment_items_by_course[course].append(item_id)
                item_id += 1
            section_id += 1

    return {
        "sections": sections,
        "section_items": section_items,
        "section_by_course": section_by_course,
        "section_course": section_course,
        "assignment_items_by_course": assignment_items_by_course,
    }


def generate_calendars_and_events(
    course_codes: list[str],
    assignment_items_by_course: dict[str, list[int]],
) -> dict[str, Any]:
    """Generate one course calendar per course plus general and item-linked events."""
    print("Generating calendars and events...")
    event_titles = [
        "Lecture", "Tutorial", "Lab Session", "Office Hours", "Quiz",
        "Midterm Exam", "Final Exam", "Assignment Due", "Project Submission",
        "Guest Lecture", "Study Group", "Review Session", "Workshop", "Seminar",
    ]

    calendars: list[tuple[Any, ...]] = []
    calendar_by_course: dict[str, int] = {}
    events: list[tuple[Any, ...]] = []
    calendar_id = 1
    event_id = 1

    for course in course_codes:
        calendars.append((calendar_id, course))
        calendar_by_course[course] = calendar_id
        for _ in range(random.randint(8, 15)):
            event_date = fake.date_between(start_date="-1y", end_date="+6m")
            title = random.choice(event_titles)
            assignment_items = assignment_items_by_course[course]
            section_item_id = random.choice(assignment_items) if assignment_items and random.random() > 0.5 else None
            events.append((event_id, calendar_id, event_date, title, section_item_id))
            event_id += 1
        calendar_id += 1

    return {
        "calendars": calendars,
        "calendar_by_course": calendar_by_course,
        "calendar_events": events,
    }


def generate_submissions_and_course_grades(
    course_codes: list[str],
    course_students: dict[str, set[int]],
    assignment_items_by_course: dict[str, list[int]],
    enrol_pairs: list[tuple[int, str]],
) -> dict[str, Any]:
    """Generate assignment submissions and derive Enrol.grade from graded submissions."""
    print("Generating submissions and course grades...")
    submissions: list[tuple[Any, ...]] = []
    course_grade_scores: dict[tuple[int, str], list[int]] = defaultdict(list)
    submission_id = 1

    for course in course_codes:
        assignment_items = assignment_items_by_course[course]
        if not assignment_items:
            continue
        sampled_students = random.sample(
            sorted(course_students[course]),
            min(30, len(course_students[course])),
        )
        for sid in sampled_students:
            submission_count = max(1, int(len(assignment_items) * random.uniform(0.5, 1.0)))
            chosen_items = random.sample(assignment_items, min(submission_count, len(assignment_items)))
            for section_item_id in chosen_items:
                text = clean_text(fake.sentence(nb_words=20), 200)
                submitted_at = fake.date_between(start_date="-1y", end_date="today")
                grade = random.randint(40, 100) if random.random() > 0.1 else None
                if grade is not None:
                    course_grade_scores[(sid, course)].append(grade)
                submissions.append((submission_id, sid, section_item_id, text, None, submitted_at, grade))
                submission_id += 1

    enrol_rows: list[tuple[Any, ...]] = []
    for sid, course in enrol_pairs:
        grades = course_grade_scores.get((sid, course), [])
        course_grade = int((sum(grades) / len(grades)) + 0.5) if grades else None
        enrol_rows.append((sid, course, course_grade))

    return {
        "submissions": submissions,
        "enrol_rows": enrol_rows,
        "course_grade_scores": course_grade_scores,
    }


# ---------------------------------------------------------------------------
# Validation and output
# ---------------------------------------------------------------------------

def ensure_unique(values: list[Any], label: str) -> None:
    """Raise a clear validation error when generated key-like values repeat."""
    counts = Counter(values)
    duplicates = [value for value, count in counts.items() if count > 1]
    if duplicates:
        raise ValueError(f"Duplicate {label}: {duplicates[:5]}")


def validate_dataset(data: dict[str, Any]) -> None:
    """Validate coursework constraints and foreign-key consistency before writing SQL."""
    print("Validating generated dataset...")
    users = data["users"]
    courses = data["courses"]
    course_codes = data["course_codes"]
    student_ids = set(data["student_ids"])
    lecturer_ids = set(data["lecturer_ids"])
    admin_ids = set(data["admin_ids"])
    student_courses = data["student_courses"]
    course_students = data["course_students"]
    lecturer_courses = data["lecturer_courses"]
    course_lecturer = data["course_lecturer"]
    teaches = data["teaches"]
    sections = data["sections"]
    section_items = data["section_items"]
    calendars = data["calendars"]
    calendar_events = data["calendar_events"]
    submissions = data["submissions"]
    enrol_rows = data["enrol_rows"]
    course_grade_scores = data["course_grade_scores"]

    role_counts = Counter(row[4] for row in users)
    if role_counts["student"] != NUM_STUDENTS:
        raise ValueError(f"Expected {NUM_STUDENTS} students, found {role_counts['student']}")
    if role_counts["lecturer"] != NUM_LECTURERS:
        raise ValueError(f"Expected {NUM_LECTURERS} lecturers, found {role_counts['lecturer']}")
    if role_counts["admin"] != NUM_ADMINS:
        raise ValueError(f"Expected {NUM_ADMINS} admins, found {role_counts['admin']}")
    if len(courses) < 200:
        raise ValueError("At least 200 courses are required")

    user_ids = [row[0] for row in users]
    ensure_unique(user_ids, "userID")
    ensure_unique([row[3] for row in users], "email")
    ensure_unique(course_codes, "courseCode")
    ensure_unique([row[1] for row in courses], "courseName")

    if any(not COURSE_CODE_RE.fullmatch(course_code) for course_code in course_codes):
        raise ValueError("All course codes must be exactly 8 uppercase alphanumeric characters")

    for sid in student_ids:
        count = len(student_courses[sid])
        if not MIN_STUDENT_COURSES <= count <= MAX_STUDENT_COURSES:
            raise ValueError(f"Student {sid} has {count} courses")

    for course in course_codes:
        if len(course_students[course]) < MIN_COURSE_STUDENTS:
            raise ValueError(f"Course {course} has fewer than {MIN_COURSE_STUDENTS} students")
        if course not in course_lecturer:
            raise ValueError(f"Course {course} has no lecturer")

    for lecturer in lecturer_ids:
        count = len(lecturer_courses[lecturer])
        if not MIN_LECTURER_COURSES <= count <= MAX_LECTURER_COURSES:
            raise ValueError(f"Lecturer {lecturer} has {count} courses")

    ensure_unique([row[1] for row in teaches], "Teaches.courseCode")
    if sum(1 for courses_for_lecturer in lecturer_courses.values() if len(courses_for_lecturer) >= 3) == 0:
        raise ValueError("At least one lecturer must teach 3+ courses for reporting")

    section_ids = {row[0] for row in sections}
    section_item_ids = {row[0] for row in section_items}
    calendar_ids = {row[0] for row in calendars}
    ensure_unique(list(section_ids), "secID")
    ensure_unique(list(section_item_ids), "secItemID")
    ensure_unique(list(calendar_ids), "calendarID")
    ensure_unique([row[0] for row in calendar_events], "eventID")
    ensure_unique([row[0] for row in submissions], "subID")

    for _, section_id, _, _, _, item_type, due_date in section_items:
        if section_id not in section_ids:
            raise ValueError(f"Section item references missing section {section_id}")
        if item_type not in ITEM_TYPES:
            raise ValueError(f"Invalid item type {item_type}")
        if item_type != "assignment" and due_date is not None:
            raise ValueError("Only assignment section items may have due dates")

    for _, calendar_id, _, _, section_item_id in calendar_events:
        if calendar_id not in calendar_ids:
            raise ValueError(f"Calendar event references missing calendar {calendar_id}")
        if section_item_id is not None and section_item_id not in section_item_ids:
            raise ValueError(f"Calendar event references missing section item {section_item_id}")

    assignment_item_ids = {row[0] for row in section_items if row[5] == "assignment"}
    for _, sid, section_item_id, _, _, _, grade in submissions:
        if sid not in student_ids:
            raise ValueError(f"Submission references non-student user {sid}")
        if section_item_id not in assignment_item_ids:
            raise ValueError(f"Submission references non-assignment item {section_item_id}")
        if grade is not None and not 0 <= grade <= 100:
            raise ValueError(f"Invalid submission grade {grade}")

    enrol_lookup = {(row[0], row[1]): row[2] for row in enrol_rows}
    if len(enrol_lookup) != len(enrol_rows):
        raise ValueError("Duplicate Enrol rows generated")
    for sid, course in enrol_lookup:
        if sid not in student_ids:
            raise ValueError(f"Enrollment references non-student user {sid}")
        if course not in course_codes:
            raise ValueError(f"Enrollment references missing course {course}")
        grades = course_grade_scores.get((sid, course), [])
        expected = int((sum(grades) / len(grades)) + 0.5) if grades else None
        if enrol_lookup[(sid, course)] != expected:
            raise ValueError(f"Enrollment grade mismatch for {sid}/{course}")
        if expected is not None and not 0 <= expected <= 100:
            raise ValueError(f"Invalid enrollment grade {expected}")


def build_dataset() -> dict[str, Any]:
    """Run all generation phases and merge their outputs into one dataset dict."""
    user_data = generate_users()
    course_data = generate_courses()
    teaching_data = assign_lecturers(user_data["lecturer_ids"], course_data["course_codes"])
    enrollment_data = enroll_students(user_data["student_ids"], course_data["course_codes"])
    discussion_data = generate_forums_and_threads(
        course_data["course_codes"],
        enrollment_data["course_students"],
        teaching_data["course_lecturer"],
    )
    section_data = generate_sections_and_items(course_data["course_codes"])
    calendar_data = generate_calendars_and_events(
        course_data["course_codes"],
        section_data["assignment_items_by_course"],
    )
    submission_data = generate_submissions_and_course_grades(
        course_data["course_codes"],
        enrollment_data["course_students"],
        section_data["assignment_items_by_course"],
        enrollment_data["enrol_pairs"],
    )

    data: dict[str, Any] = {}
    for chunk in (
        user_data,
        course_data,
        teaching_data,
        enrollment_data,
        discussion_data,
        section_data,
        calendar_data,
        submission_data,
    ):
        data.update(chunk)
    return data


def write_sql(data: dict[str, Any]) -> None:
    """Overwrite generated_seed.sql with INSERT statements for real tables only."""
    print(f"Writing {OUTPUT_FILE}...")
    with open(OUTPUT_FILE, "w", encoding="utf-8", newline="\n") as handle:
        handle.write("-- ================================================================\n")
        handle.write("-- VLE Database Population Script\n")
        handle.write(f"-- Students:{NUM_STUDENTS:,}  Lecturers:{NUM_LECTURERS}  Courses:{NUM_COURSES}\n")
        handle.write("-- Run database/schema.sql before this file.\n")
        handle.write("-- CourseMember is a view derived from Enrol and Teaches.\n")
        handle.write("-- ================================================================\n\n")
        handle.write("SET FOREIGN_KEY_CHECKS = 0;\n")
        handle.write("SET UNIQUE_CHECKS = 0;\n")
        handle.write("SET autocommit = 0;\n\n")

        sections = [
            ("UserAccount", ["userID", "fname", "lname", "email", "accessLvl", "password"], data["users"]),
            ("Course", ["courseCode", "courseName", "department"], data["courses"]),
            ("Teaches", ["userID", "courseCode"], data["teaches"]),
            ("DiscussionForum", ["dfID", "dfname", "courseCode"], data["forums"]),
            (
                "DiscussionThread",
                ["dtID", "dfID", "parentpostID", "userID", "threadbody", "topic", "date_created"],
                data["threads"],
            ),
            ("CourseSection", ["secID", "secName", "courseCode"], data["sections"]),
            (
                "SectionItems",
                ["secItemID", "secID", "title", "secBody", "secContent", "itemtype", "dueDate"],
                data["section_items"],
            ),
            ("CourseCalendar", ["calendarID", "courseCode"], data["calendars"]),
            (
                "CalendarEvents",
                ["eventID", "calendarID", "eventDate", "eventTitle", "secItemID"],
                data["calendar_events"],
            ),
            ("Enrol", ["userID", "courseCode", "grade"], data["enrol_rows"]),
            (
                "Submission",
                ["subID", "userID", "secItemID", "subText", "subContent", "submDate", "grade"],
                data["submissions"],
            ),
        ]

        for table, columns, rows in sections:
            handle.write(f"-- {table}\n")
            write_insert_batches(handle, table, columns, rows)
            handle.write("\n")

        handle.write("COMMIT;\n")
        handle.write("SET FOREIGN_KEY_CHECKS = 1;\n")
        handle.write("SET UNIQUE_CHECKS = 1;\n")
        handle.write("SET autocommit = 1;\n")


def write_demo_credentials(data: dict[str, Any]) -> None:
    """Write known synthetic credentials for one seed student, lecturer, and admin."""
    print(f"Writing {DEMO_CREDENTIALS_FILE}...")
    user_lookup = data["user_lookup"]
    demo_users = [
        ("Student", STUDENT_START_ID),
        ("Lecturer", LECTURER_START_ID),
        ("Admin", ADMIN_START_ID),
    ]

    lines = [
        "Seed-data demo credentials only",
        "",
        "These are synthetic accounts from database/generated_seed.sql for local Postman/demo testing.",
        "Do not use this file for real user credentials.",
        "",
        "New accounts created through POST /users/register return their generated password once.",
        "Those runtime plaintext passwords are not stored in UserAccount and cannot be queried later.",
        "",
    ]

    for label, user_id in demo_users:
        user = user_lookup[user_id]
        lines.extend([
            label,
            f"userID: {user['userID']}",
            f"name: {user['fname']} {user['lname']}",
            f"email: {user['email']}",
            f"password: {user['password']}",
            "",
        ])

    with open(DEMO_CREDENTIALS_FILE, "w", encoding="utf-8", newline="\n") as handle:
        handle.write("\n".join(lines).rstrip() + "\n")


def print_summary(data: dict[str, Any]) -> None:
    """Print a short generation summary for the teammate running the script."""
    size_mb = os.path.getsize(OUTPUT_FILE) / 1024 / 1024
    lecturer_loads = [len(courses) for courses in data["lecturer_courses"].values()]
    student_loads = [len(courses) for courses in data["student_courses"].values()]
    course_student_counts = [len(students) for students in data["course_students"].values()]

    print(f"\nDone -> {OUTPUT_FILE}")
    print(f"    File size       : {size_mb:.1f} MB")
    print(f"    Students        : {NUM_STUDENTS:,}")
    print(f"    Lecturers       : {NUM_LECTURERS}")
    print(f"    Admins          : {NUM_ADMINS}")
    print(f"    Courses         : {len(data['courses'])}")
    print(f"    Enrollments     : {len(data['enrol_rows']):,}")
    print(f"    Forums          : {len(data['forums']):,}")
    print(f"    Threads         : {len(data['threads']):,}")
    print(f"    Section items   : {len(data['section_items']):,}")
    print(f"    Calendar events : {len(data['calendar_events']):,}")
    print(f"    Submissions     : {len(data['submissions']):,}")
    print(f"    Student load    : {min(student_loads)}-{max(student_loads)} courses")
    print(f"    Course students : {min(course_student_counts)}-{max(course_student_counts)} students")
    print(f"    Lecturer load   : {min(lecturer_loads)}-{max(lecturer_loads)} courses")


def main() -> None:
    """Entrypoint used when running python database/generate_seed_data.py."""
    random.seed(RANDOM_SEED)
    Faker.seed(RANDOM_SEED)
    data = build_dataset()
    validate_dataset(data)
    write_sql(data)
    write_demo_credentials(data)
    print_summary(data)


if __name__ == "__main__":
    main()
