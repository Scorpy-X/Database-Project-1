DROP DATABASE IF EXISTS Vle; 
CREATE DATABASE Vle;
USE Vle;

-- Users

CREATE TABLE UserAccount(
    userID INT PRIMARY KEY, -- userID is 9 digits long ( 620 students, 200 - staff, 111 - admin )
    fname VARCHAR(50) NOT NULL,
    lname VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    accessLvl ENUM('student','lecturer','admin') NOT NULL, -- They go to uwi and uwi makes the account for them
    password VARCHAR(100) NOT NULL
);

-- Courses
CREATE TABLE Course(
    courseCode VARCHAR(8) PRIMARY KEY,
    courseName VARCHAR(50) NOT NULL UNIQUE,
    department VARCHAR(50) NOT NULL,
    CHECK (CHAR_LENGTH(courseCode) = 8),
    CHECK (courseCode REGEXP '^[A-Z0-9]{8}$')
);

-- Discussion Forums
CREATE TABLE DiscussionForum(
    dfID INT PRIMARY KEY AUTO_INCREMENT,
    dfname VARCHAR(50) NOT NULL,
    courseCode VARCHAR(8) NOT NULL,
    FOREIGN KEY (courseCode) REFERENCES Course(courseCode) ON DELETE CASCADE
);

-- Discussion Threads
CREATE TABLE DiscussionThread(
    dtID INT PRIMARY KEY AUTO_INCREMENT, -- Added Auto Increment
    dfID INT NOT NULL, 
    parentpostID INT NULL,
    userID INT NOT NULL,
    threadbody VARCHAR(500),
    topic VARCHAR(20),
    date_created DATE,
    FOREIGN KEY (dfID) REFERENCES DiscussionForum(dfID) ON DELETE CASCADE,
    FOREIGN KEY (userID) REFERENCES UserAccount(userID) ON DELETE CASCADE,
    FOREIGN KEY (parentpostID) REFERENCES DiscussionThread(dtID) ON DELETE CASCADE
);

-- Sections
CREATE TABLE CourseSection(
    secID INT PRIMARY KEY AUTO_INCREMENT,
    secName VARCHAR(50) NOT NULL,
    courseCode VARCHAR(8) NOT NULL,
    FOREIGN KEY (courseCode) REFERENCES Course(courseCode) ON DELETE CASCADE
);

-- Section Items
CREATE TABLE SectionItems(
    secItemID INT PRIMARY KEY AUTO_INCREMENT, -- Added Auto Increment
    secID INT NOT NULL,
    title VARCHAR(50),
    secBody VARCHAR(500),
    secContent TEXT,
    itemtype ENUM('assignment', 'link', 'file', 'slide') NOT NULL,
    dueDate DATE,
    FOREIGN KEY (secID) REFERENCES CourseSection(secID) ON DELETE CASCADE
);

-- Course Calendar
CREATE TABLE CourseCalendar(
    calendarID INT PRIMARY KEY AUTO_INCREMENT,   -- calendarID rename
    courseCode VARCHAR(8) NOT NULL UNIQUE,
    FOREIGN KEY (courseCode) REFERENCES Course(courseCode) ON DELETE CASCADE
);

-- Calendar Events
CREATE TABLE CalendarEvents(
    eventID INT PRIMARY KEY AUTO_INCREMENT, -- Added Auto Increment , calendarID rename 
    calendarID INT NOT NULL,
    eventDate DATE,
    eventTitle VARCHAR(50),
    secItemID INT,
    FOREIGN KEY (calendarID) REFERENCES CourseCalendar(calendarID) ON DELETE CASCADE,
    FOREIGN KEY (secItemID) REFERENCES SectionItems(secItemID) ON DELETE CASCADE
);

-- Submissions
CREATE TABLE Submission(
    subID INT PRIMARY KEY AUTO_INCREMENT, -- Added Auto Increment 
    userID INT NOT NULL,
    secItemID INT NOT NULL,
    subText VARCHAR(200),
    subContent TEXT, -- Text/metadata submission content; real file upload is out of scope
    submDate DATE,
    grade INT,
    FOREIGN KEY (userID) REFERENCES UserAccount(userID) ON DELETE CASCADE,
    FOREIGN KEY (secItemID) REFERENCES SectionItems(secItemID) ON DELETE CASCADE,
    CHECK (grade IS NULL OR grade BETWEEN 0 AND 100)
);

-- Enrollment
CREATE TABLE Enrol(
    userID INT NOT NULL,
    courseCode VARCHAR(8) NOT NULL,
    grade INT,
    FOREIGN KEY (userID) REFERENCES UserAccount(userID) ON DELETE CASCADE,
    FOREIGN KEY (courseCode) REFERENCES Course(courseCode) ON DELETE CASCADE,
    PRIMARY KEY (userID, courseCode),
    CHECK (grade IS NULL OR grade BETWEEN 0 AND 100)
);

-- Teaching Assignment
CREATE TABLE Teaches(
    userID INT NOT NULL,
    courseCode VARCHAR(8) NOT NULL,
    FOREIGN KEY (userID) REFERENCES UserAccount(userID) ON DELETE CASCADE,
    FOREIGN KEY (courseCode) REFERENCES Course(courseCode) ON DELETE CASCADE,
    PRIMARY KEY (userID, courseCode),
    UNIQUE (courseCode)
);

-- Calendar Event Views
CREATE VIEW course_calendar_events AS
SELECT
    c.courseCode,
    c.courseName,
    ce.eventID,
    ce.calendarID,
    ce.eventDate,
    ce.eventTitle,
    ce.secItemID
FROM Course c
JOIN CourseCalendar cc ON c.courseCode = cc.courseCode
JOIN CalendarEvents ce ON cc.calendarID = ce.calendarID;

CREATE VIEW student_calendar_events AS
SELECT
    e.userID,
    c.courseCode,
    c.courseName,
    ce.eventID,
    ce.calendarID,
    ce.eventDate,
    ce.eventTitle,
    ce.secItemID
FROM Enrol e
JOIN Course c ON e.courseCode = c.courseCode
JOIN CourseCalendar cc ON c.courseCode = cc.courseCode
JOIN CalendarEvents ce ON cc.calendarID = ce.calendarID;

-- Course Membership View (derived from enrollment and teaching assignments)
CREATE VIEW CourseMember AS -- Fixed error in Postman that prevented comparison 
SELECT 
    userID,
    CAST('student' AS CHAR CHARACTER SET utf8mb4)
        COLLATE utf8mb4_0900_ai_ci AS memberRole,
    courseCode
FROM Enrol

UNION ALL

SELECT 
    userID,
    CAST('lecturer' AS CHAR CHARACTER SET utf8mb4)
        COLLATE utf8mb4_0900_ai_ci AS memberRole,
    courseCode
FROM Teaches;


-- INDEXES 

-- UserAccount: Filter by access level )
CREATE INDEX idx_user_accesslvl ON UserAccount(accessLvl);

-- DiscussionForum: Get forums by course
CREATE INDEX idx_discussionforum_coursecode ON DiscussionForum(courseCode);

-- DiscussionThread: Get top-level threads (dfID + parentpostID IS NULL queries)
CREATE INDEX idx_discussionthread_df_parent ON DiscussionThread(dfID, parentpostID);

-- DiscussionThread: Get replies to a specific post
CREATE INDEX idx_discussionthread_parentpost ON DiscussionThread(parentpostID);

-- DiscussionThread: Get posts by user
CREATE INDEX idx_discussionthread_user ON DiscussionThread(userID);

-- DiscussionThread: Sort by date
CREATE INDEX idx_discussionthread_date ON DiscussionThread(date_created);

-- CourseSection: Get sections by course
CREATE INDEX idx_coursesection_coursecode ON CourseSection(courseCode);

-- SectionItems: Get items by section
CREATE INDEX idx_sectionitems_secid ON SectionItems(secID);

-- CalendarEvents: Get events by calendar
CREATE INDEX idx_calendarevents_calendarid ON CalendarEvents(calendarID);

-- CalendarEvents: Filter events by date
CREATE INDEX idx_calendarevents_date ON CalendarEvents(eventDate);

-- CalendarEvents: Link events to section items
CREATE INDEX idx_calendarevents_secitem ON CalendarEvents(secItemID);


-- TO SPEED UP THE REPORT VIEWS 
CREATE INDEX idx_enrol_coursecode ON Enrol(courseCode);
CREATE INDEX idx_enrol_userid ON Enrol(userID);
CREATE INDEX idx_teaches_userid ON Teaches(userID);

CREATE INDEX idx_enrol_userid_grade ON Enrol(userID, grade);
CREATE INDEX idx_useraccount_accesslvl_userid ON UserAccount(accessLvl, userID);