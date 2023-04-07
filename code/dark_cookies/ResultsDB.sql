BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "dialogs" (
	"domain"	TEXT,
	"dialog_num"	INTEGER,
	"checked"	TEXT,
	"capture_type"	TEXT,
	"score"	REAL,
	"css_selector"	TEXT,
	"text"	TEXT,
	"raw_html"	TEXT,
	"screenshot"	BLOB,
	"cmp"	TEXT,
	PRIMARY KEY("domain","dialog_num")
);
CREATE TABLE IF NOT EXISTS "websites" (
	"domain"	TEXT,
	"status"	TEXT,
	"location"	TEXT,
	"timestamp"	TEXT,
	"time"	TEXT,
	"category"	TEXT,
	"curlie_category"	TEXT,
	"homepage2vec_category"	INTEGER,
	PRIMARY KEY("domain")
);
CREATE TABLE IF NOT EXISTS "cookie_collections" (
	"collection_num"	INTEGER,
	"domain"	TEXT,
	"type"	TEXT,
	"num_cookies"	INTEGER,
	"timestamp"	TEXT,
	"num_id_like"	INTEGER,
	"num_first_party"	INTEGER,
	"num_third_party"	INTEGER,
	PRIMARY KEY("collection_num")
);
CREATE TABLE IF NOT EXISTS "dark_patterns" (
	"domain"	TEXT,
	"type"	TEXT,
	"value"	TEXT,
	"auto_value"	TEXT,
	PRIMARY KEY("domain","type")
);
CREATE TABLE IF NOT EXISTS "clickables" (
	"domain"	TEXT,
	"clickable_num"	INTEGER,
	"dialog_num"	TEXT,
	"auto_type"	TEXT,
	"type"	TEXT,
	"css_selector"	TEXT,
	"text"	TEXT,
	"raw_html"	TEXT,
	"screenshot"	BLOB,
	PRIMARY KEY("domain","clickable_num")
);
CREATE TABLE IF NOT EXISTS "cookies" (
	"collection_num"	INTEGER,
	"cookie_num"	INTEGER,
	"name"	TEXT,
	"value"	TEXT,
	"domain"	TEXT,
	"path"	TEXT,
	"expires"	TEXT,
	"size"	TEXT,
	"httponly"	TEXT,
	"secure"	TEXT,
	"samesite"	TEXT,
	"raw_cookie"	TEXT,
	PRIMARY KEY("collection_num","cookie_num")
);
COMMIT;
