-- DB Version: 2
CREATE TABLE IF NOT EXISTS "habit" (
    "id" INTEGER NOT NULL PRIMARY KEY,
    "name" VARCHAR(255) NOT NULL,
    "created_date" DATE NOT NULL,
    "frequency" INTEGER NOT NULL,
    "quantum" REAL NOT NULL,
    "units" VARCHAR(255) NOT NULL,
    "magica" TEXT NOT NULL,
    "active" INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS "activity" (
    "id" INTEGER NOT NULL PRIMARY KEY,
    "for_habit_id" INTEGER NOT NULL,
    "quantum" REAL NOT NULL,
    "update_date" DATETIME NOT NULL,
    FOREIGN KEY ("for_habit_id") REFERENCES "habit" ("id")
);

CREATE TABLE IF NOT EXISTS "config" (
    "id" INTEGER NOT NULL PRIMARY KEY,
    "name" VARCHAR(255) NOT NULL,
    "value" VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS "summary" (
    "id" INTEGER NOT NULL PRIMARY KEY,
    "for_habit_id" INTEGER NOT NULL,
    "target" REAL NOT NULL,
    "target_date" DATE NOT NULL,
    "streak" INTEGER NOT NULL,
    FOREIGN KEY ("for_habit_id") REFERENCES "habit" ("id")
);

CREATE INDEX "activitymodel_for_habit_id" ON "activity" ("for_habit_id");
CREATE UNIQUE INDEX "config_name" ON "config" ("name");
CREATE INDEX "summary_for_habit_id" ON "summary" ("for_habit_id");

-- Insert test data
INSERT INTO "habit" ("id", "name", "created_date", "frequency", "quantum", "units", "magica", "active")
VALUES (1, "habit 1", date('now'), 1, 10.0, "units", "sample pledge", 1),
(2, "habit 2", date('now'), 1, 10.0, "units", "sample pledge2", 1);

INSERT INTO "activity" ("id", "for_habit_id", "quantum", "update_date")
VALUES (1, 1, 11.0, date('now', '-1 days')),
(2, 1, 10.0, date('now', '-2 days')),
(3, 2, 11.0, date('now', '-1 days')),
(4, 2, 10.0, date('now', '-3 days'));

INSERT INTO summary ("id", "for_habit_id", "target", "target_date", "streak")
VALUES (1, 1, 0.0, date('now'), 2),
(2, 2, 0.0, date('now'), 1);

INSERT INTO config VALUES(2,'version','2');
