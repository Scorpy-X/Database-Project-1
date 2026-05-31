-- Demo queries for presentation - Monday 2026-05-18
USE Vle;

-- a) At least 100,000 students
-- Check: total number of student accounts
-- Expected: at least 100,000
SELECT COUNT(*) AS total_students
FROM UserAccount
WHERE accessLvl = 'student';

-- b) At least 200 courses
-- Check: total number of courses
-- Expected: at least 200
SELECT COUNT(*) AS total_courses
FROM Course;

-- c) No student can take more than 6 courses
-- Check: students violating the maximum course limit
-- Expected: no rows
SELECT userID, COUNT(*) AS course_count
FROM Enrol
GROUP BY userID
HAVING COUNT(*) > 6;

-- d) A student must be enrolled in at least 3 courses
-- Check 1: students violating the minimum course requirement
-- Expected: no rows
SELECT u.userID, COUNT(e.courseCode) AS course_count
FROM UserAccount u
LEFT JOIN Enrol e ON u.userID = e.userID
WHERE u.accessLvl = 'student'
GROUP BY u.userID
HAVING COUNT(e.courseCode) < 3;

-- d) A student must be enrolled in at least 3 courses
-- Check 2: number of students meeting the minimum course requirement
-- Expected: most students counted
SELECT COUNT(*) AS students_with_at_least_3_courses
FROM (
    SELECT u.userID
    FROM UserAccount u
    JOIN Enrol e ON u.userID = e.userID
    WHERE u.accessLvl = 'student'
    GROUP BY u.userID
    HAVING COUNT(e.courseCode) >= 3
) AS eligible_students;

-- e) Each course must have at least 10 members
-- Check: courses violating the minimum enrolment requirement
-- Expected: no rows
SELECT courseCode, COUNT(*) AS member_count
FROM Enrol
GROUP BY courseCode
HAVING COUNT(*) < 10;

-- f) No lecturer can teach more than 5 courses
-- Check: lecturers violating the maximum teaching load
-- Expected: no rows
SELECT userID, COUNT(*) AS course_count
FROM Teaches
GROUP BY userID
HAVING COUNT(*) > 5;

-- g) A lecturer must teach at least 1 course
-- Check 1: lecturers violating the minimum teaching requirement
-- Expected: no rows
SELECT u.userID
FROM UserAccount u
LEFT JOIN Teaches t ON u.userID = t.userID
WHERE u.accessLvl = 'lecturer'
GROUP BY u.userID
HAVING COUNT(t.courseCode) = 0;

-- g) A lecturer must teach at least 1 course
-- Check 2: number of lecturers meeting the minimum teaching requirement
-- Expected: most lecturers counted
SELECT COUNT(*) AS lecturers_teaching_at_least_1_course
FROM (
    SELECT u.userID
    FROM UserAccount u
    JOIN Teaches t ON u.userID = t.userID
    WHERE u.accessLvl = 'lecturer'
    GROUP BY u.userID
    HAVING COUNT(t.courseCode) >= 1
) AS active_lecturers;
