CREATE TABLE sections(
course_num INTEGER NOT NULL PRIMARY KEY,
section_type TEXT NOT NULL,
section_num INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE names(
course_num INTEGER NOT NULL PRIMARY KEY,
course_name TEXT NOT NULL,
topic TEXT NOT NULL,
dept TEXT NOT NULL,
catalog_num TEXT NOT NULL
);