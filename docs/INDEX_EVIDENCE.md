# Index Evidence

The index set in `database/schema.sql` is based on route and report access patterns, not on indexing every foreign key or every sortable column. The goal is a practical schema that is easy to defend and avoids redundant indexes already covered by primary keys or unique constraints.

## Useful Indexes

| Query Purpose | Candidate Index | EXPLAIN Key Used | Estimated Rows | Filesort/Temporary | Why It Is Useful |
| --- | --- | --- | ---: | --- | --- |
| Course roster and enrollment reports by course | `idx_enrol_coursecode` | `idx_enrol_coursecode` | 1606 | No | `Enrol` primary key is `(userID, courseCode)`, so course-first lookups need a separate course index. |
| Role-filtered student report joined by user id | `idx_useraccount_accesslvl_userid` | `idx_useraccount_accesslvl_userid` | 49739 | Yes on aggregate report | Filters users by role before joining on `userID`; report aggregation can still require temporary sorting. |
| Course sections in section order | `idx_coursesection_coursecode_secid` | `idx_coursesection_coursecode_secid` | 5 | No | Supports `WHERE courseCode = ? ORDER BY secID`. |
| Section items in item order | `idx_sectionitems_secid_secitemid` | `idx_sectionitems_secid_secitemid` | 5 | No | Supports loading items for one section in stable item order. |
| Forums for a course | `idx_discussionforum_coursecode` | `idx_discussionforum_coursecode` | 2 | No | Supports course forum lookup. |
| Top-level forum threads by forum | `idx_discussionthread_forum_threads` | `idx_discussionthread_forum_threads` | 3 | No for the simple list | Supports `dfID`, `parentpostID`, and newest-first ordering. |
| Reply lookup/counting | `idx_discussionthread_parent_forum` | `idx_discussionthread_parent_forum` | 2 | No | Supports the reply side of the forum thread count join. |
| Calendar events by calendar/date | `idx_calendarevents_calendar_date_event` | `idx_calendarevents_calendar_date_event` | 15 | No | Supports calendar-specific event lookup and date ordering. |
| Assignment submissions by item/date | `idx_submission_item_date` | `idx_submission_item_date` | 30 | No | Supports submissions for one assignment, newest first. |

Some report queries still use temporary tables or filesort because aggregation and ordering by computed values are expected for those reports. The indexes reduce lookup and join work; they do not remove every sort from aggregate reports.

## Rejected Indexes

| Rejected Candidate | EXPLAIN Evidence | Why It Was Rejected |
| --- | --- | --- |
| `idx_enrol_userid` on `Enrol(userID)` | `WHERE userID = ?` selected `PRIMARY`, estimated 6 rows. | Redundant. `PRIMARY KEY (userID, courseCode)` already starts with `userID`. |
| `idx_teaches_userid` on `Teaches(userID)` | Lecturer-course lookup is covered by `PRIMARY`. | Redundant. `PRIMARY KEY (userID, courseCode)` already starts with `userID`. |
| `idx_user_accesslvl` on `UserAccount(accessLvl)` | Role report queries selected `idx_useraccount_accesslvl_userid`. | Covered by the composite index, which starts with `accessLvl`. |
| `idx_discussionthread_date` on `DiscussionThread(date_created)` | Forum list queries selected `idx_discussionthread_forum_threads`, not a standalone date index. | Weak for this app. The app does not list all threads globally by date; it lists threads within one forum. |
| `idx_calendarevents_date` on `CalendarEvents(eventDate)` | Calendar routes selected `idx_calendarevents_calendar_date_event`. | Weak alone. Calendar routes usually filter by calendar/course first, then order or filter by date. |

## How To Recheck

After rebuilding the database, run representative `EXPLAIN` statements against the route queries. Useful signs:

- `key` uses the intended index.
- `rows` is small relative to the table size.
- `type` is `const`, `eq_ref`, `ref`, or `range` rather than `ALL`.
- `Using filesort` and `Using temporary` are absent for simple lookup/order queries, though they may remain for aggregate reports.
