-- reflect.sql: the same log, asked in SQL. The columns match what Mind.save() writes.
-- SQL is declarative: you state what you want, the engine decides how.
-- Lines starting with -- are comments. Statements end with a semicolon.

CREATE TABLE log (
    id          INTEGER,
    "when"      TEXT,      -- quoted because WHEN is a reserved SQL word
    subject     TEXT,
    observation TEXT,
    measure     INTEGER,
    doubt       TEXT,
    struggle    TEXT,
    resolved    INTEGER    -- 0 open, 1 resolved (SQLite has no boolean type)
);

-- In the sqlite3 shell, ".import --csv --skip 1 log.csv log" loads the file instead.
INSERT INTO log VALUES
 (0,'2026-11-02','example mood','heavy day',7,NULL,NULL,0),
 (1,'2026-11-03','example mood','lighter day',5,NULL,NULL,0),
 (2,'2026-11-04','example mood','heavy and long then relaxed',4,'state or relief?',NULL,0);

-- select: one subject (pandas: log[log["subject"] == "example mood"])
SELECT * FROM log WHERE subject = 'example mood';

-- group: average measure per subject (pandas: groupby("subject")["measure"].mean())
SELECT subject, AVG(measure) AS average FROM log GROUP BY subject ORDER BY average DESC;

-- open doubts (pandas: log[log["doubt"].notna() & ~log["resolved"]]). NULL is tested with IS.
SELECT subject, doubt FROM log WHERE doubt IS NOT NULL AND resolved = 0;

-- order: time as the spine (pandas: sort_values("when"))
SELECT * FROM log ORDER BY "when";

-- lag: change from the entry before (pandas: diff()). A window function.
SELECT "when", measure, measure - LAG(measure) OVER (ORDER BY "when") AS change FROM log;
