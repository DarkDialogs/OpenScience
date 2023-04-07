BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "cmp_fingerprints" (
	"cmp_name"	TEXT,
	"type"	TEXT,
	"value"	TEXT
);
CREATE TABLE IF NOT EXISTS "general_element_hiding_rules" (
	"selector"	TEXT,
	"source"	TEXT,
	"date_updated"	TEXT,
	PRIMARY KEY("selector")
);
CREATE TABLE IF NOT EXISTS "specific_element_hiding_rules" (
	"url"	TEXT,
	"selector"	INTEGER,
	"source"	TEXT,
	"date_updated"	TEXT,
	PRIMARY KEY("url","selector")
);
CREATE TABLE IF NOT EXISTS "dictionaries" (
	"name"	TEXT,
	"words"	TEXT,
	"source"	TEXT,
	"date_updated"	TEXT,
	PRIMARY KEY("name","source")
);
CREATE TABLE IF NOT EXISTS "tranco_websites" (
	"rank"	INTEGER,
	"domain"	TEXT,
	"timestamp"	TEXT,
	PRIMARY KEY("rank")
);
CREATE TABLE IF NOT EXISTS "user_element_hiding_rules" (
	"url"	TEXT,
	"selector"	INTEGER,
	"source"	TEXT,
	"date_updated"	TEXT,
	PRIMARY KEY("url","selector")
);
COMMIT;
