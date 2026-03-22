-- @name: create_alumni_table
CREATE TABLE "alumni" (
	"id"	INTEGER,
	"linkedin_url"	TEXT UNIQUE,
	"full_name"	TEXT UNIQUE,
	"location"	TEXT,
	"about"	TEXT,
	"cur_role"	TEXT,
	"experience"	TEXT,
	"education"	TEXT,
	"contact_info"	TEXT,
	"shared_connections"	TEXT,
	"skills"	TEXT,
	"languages"	TEXT,
	"num_conn"	INTEGER,
	"yrs_at_cur"	INTEGER,
	"yrs_aft_grad"	INTEGER,
	"customized_mail_text"	TEXT,
	"raw_info_string"	TEXT,
	PRIMARY KEY("id")
);

-- @name: deduplicate_data
DELETE FROM alumni WHERE id NOT IN (
	SELECT MIN(id)
    FROM alumni
    GROUP BY full_name, linkedin_url
	)

-- @name: test1
SELECT * FROM alumni LIMIT 5;

-- @name: alumni_fieldnames
PRAGMA table_info(alumni)

-- @name: networking_fieldnames
PRAGMA table_info(networking)
