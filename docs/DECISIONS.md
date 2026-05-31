# VLE Design Decisions

This document explains the main design choices in the current VLE project build. It is meant for teammates who need to understand why the system looks the way it does now, what changed from simpler earlier versions, and which trade-offs were intentional.

## CourseMember As A View

**Decision**  
`CourseMember` is a database view derived from `Enrol` and `Teaches`, not a physical table with its own inserts.

**Why**  
Course membership is already implied by two source-of-truth relationships:

- students belong to a course through `Enrol`
- lecturers belong to a course through `Teaches`

Keeping a third stored table for the same concept would duplicate data and create consistency problems.

**What it means in the codebase**  
Routes can still read from `CourseMember`, but writes happen to `Enrol` and `Teaches`. The schema and generator should not try to insert directly into `CourseMember`.

**Trade-off / limitation**  
This is good for consistency, but it means `CourseMember` is read-only. Any membership change must happen through the underlying tables.

## Basic Auth Instead Of JWT For Now

**Decision**  
Protected routes currently use Basic Auth instead of JWT.

**Why**  
For local development and Postman testing, Basic Auth is faster to wire up, easier for teammates to understand, and easier to demo repeatedly without managing token issuance, expiry, and refresh behavior.

**What it means in the codebase**  
`backend/app.py` authenticates protected requests directly from `request.authorization`. The public `POST /auth/login` route remains useful as a demo credential check, but the rest of the protected API does not depend on issued tokens.

**Trade-off / limitation**  
This is a coursework/demo convenience choice, not a stronger long-term auth design. JWT is still deferred rather than fully replaced.

## Single-File API Layout

**Decision**  
The Flask API remains in a single `backend/app.py` file.

**Why**  
The current priority is teammate handoff clarity and low setup friction. For a student project, one well-structured file with section headings and helper grouping is easier to trace than a multi-module refactor done late in the project.

**What it means in the codebase**  
Helpers and routes are grouped by responsibility inside `backend/app.py`, but they are intentionally still in one place.

**Trade-off / limitation**  
This is easier to follow right now, but it would become less comfortable if the system keeps growing. A later production-style cleanup could split the API into Blueprints or modules.

## One Lecturer Per Course

**Decision**  
Each course has exactly one lecturer.

**Why**  
That matches the coursework requirement more closely and keeps the lecturer-course relationship simple to explain and validate.

**What it means in the codebase**  
`Teaches` is still the relationship table, but each `courseCode` should appear only once. Course creation and lecturer reassignment both work with a single `lecturerID`.

**Trade-off / limitation**  
This simplifies validation and reporting, but it removes team-teaching support.

## Course Grades Derived From Assignment Grades

**Decision**  
`Enrol.grade` stores the current course grade, derived from graded assignment submissions.

**Why**  
The requirement says assignment grades should contribute to the student’s final average. Keeping the derived course grade in `Enrol` makes that relationship explicit and easier to query in reports.

**What it means in the codebase**  
When a submission is graded, the relevant enrollment grade is recalculated from graded assignment submissions in that course. Reports use `Enrol.grade` instead of calculating directly from raw submissions.

**Trade-off / limitation**  
This is an unweighted average. There is no assignment weighting, override workflow, or grading history in the current schema.

## Metadata-Only Content Storage

**Decision**  
`SectionItems.secContent` and `Submission.subContent` are treated as text metadata, not real binary file upload storage.

**Why**  
That keeps the system much easier to build, seed, test, and explain. It is enough for coursework features like links, fake file references, slide references, and submission text.

**What it means in the codebase**  
Content routes accept and return text values such as URLs, paths, notes, or simple references. The generator writes text/null values, not binary payloads.

**Trade-off / limitation**  
There is no real file upload, download, MIME handling, or storage backend in this build.

## Deterministic Seed Generation

**Decision**  
Seed data is generated deterministically by `database/generate_seed_data.py`.

**Why**  
Teammates need a rebuild path that is predictable. Deterministic generation makes debugging, Postman testing, demo handoff, and report verification much easier.

**What it means in the codebase**  
`random.seed(42)` and `Faker.seed(42)` are used so the same dataset structure is produced each time. The generator validates coursework constraints before writing `database/generated_seed.sql`.

**Trade-off / limitation**  
The data is synthetic and predictable by design. That is useful for coursework demos, but it is not meant to model production randomness or privacy concerns.

## Demo Credentials Are Synthetic And Deliberate

**Decision**  
The project keeps one known student, lecturer, and admin credential set in `docs/demo_credentials.txt`.

**Why**  
This removes friction during handoff, Postman testing, and live demos. Teammates do not have to inspect the generated SQL to discover workable accounts.

**What it means in the codebase**  
The generator deliberately creates known seed accounts and writes their plaintext demo credentials to `docs/demo_credentials.txt`. Runtime-created accounts still return their plaintext password only once.

**Trade-off / limitation**  
This file is only acceptable because the accounts are synthetic and local-demo-only. It would not be acceptable for real user credentials.

## Query-Driven Indexes

**Decision**
The schema keeps indexes that match the application's actual route and report access patterns.

**Why**
Indexes are most useful when they support how the system really reads data: course rosters, course content loading, forum thread retrieval, calendar event lookup, assignment submissions, and report aggregation. Composite indexes are used where queries filter and sort through multiple columns together.

**What it means in the codebase**
`database/schema.sql` avoids explicit duplicates of primary keys, unique keys, and obvious foreign-key support indexes. For example, `Enrol(userID)` is not indexed separately because `PRIMARY KEY (userID, courseCode)` already starts with `userID`. `Teaches(courseCode)` is not indexed separately because `UNIQUE (courseCode)` already provides that lookup.

**Trade-off / limitation**
The index set is intentionally practical, not exhaustive. `EXPLAIN` should be used when adding new high-volume routes or reports to confirm MySQL is selecting useful indexes and not falling back to large table scans.
