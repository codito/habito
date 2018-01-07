-- DB Version: 1
CREATE TABLE "habitmodel" (
    "id" INTEGER NOT NULL PRIMARY KEY,
    "name" VARCHAR(255) NOT NULL,
    "created_date" DATE NOT NULL,
    "frequency" INTEGER NOT NULL,
    "quantum" REAL NOT NULL,
    "units" VARCHAR(255) NOT NULL,
    "magica" TEXT NOT NULL,
    "active" INTEGER NOT NULL
);

CREATE TABLE "activitymodel" (
    "id" INTEGER NOT NULL PRIMARY KEY,
    "for_habit_id" INTEGER NOT NULL,
    "quantum" REAL NOT NULL,
    "update_date" DATETIME NOT NULL,
    FOREIGN KEY ("for_habit_id") REFERENCES "habitmodel" ("id")
);

CREATE INDEX "activitymodel_for_habit_id" ON "activitymodel" ("for_habit_id");

-- Insert test data
INSERT INTO "habitmodel" ("id", "name", "created_date", "frequency", "quantum", "units", "magica", "active")
VALUES (1, "habit 1", date('now'), 1, 10.0, "units", "sample pledge", 1),
(2, "habit 2", date('now'), 1, 10.0, "units", "sample pledge2", 1);

INSERT INTO "activitymodel" ("id", "for_habit_id", "quantum", "update_date")
VALUES (1, 1, 11.0, date('now', '-1 days')),
(2, 1, 10.0, date('now', '-2 days')),
(3, 2, 11.0, date('now', '-1 days')),
(4, 2, 10.0, date('now', '-3 days'));
