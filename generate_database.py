import sqlite3 

from utils import *

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def create_connection(db_file = DATA_BASE_FILE_PATH):
	""" create a database connection to the SQLite database specified by db_file
	:param db_file: database file
	:return: Connection object or None
	"""
	conn = None
 
	try:
		conn = sqlite3.connect(db_file)
		print(f"Database {db_file} formed.")
	except sqlite3.Error as e:
		print(e)
  
	return conn

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def create_table(conn, create_table_sql):
	""" create a table from the create_table_sql statement
	:param conn: Connection object
	:param create_table_sql: a CREATE TABLE statement
	:return:
	"""
	try:
		c = conn.cursor()
		c.execute(create_table_sql)
	except sqlite3.Error as e:
		print('Error creating table: ', e)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def create_journal_table(conn):
	journal_table = """CREATE TABLE IF NOT EXISTS journal (
		id INTEGER PRIMARY KEY,
		title TEXT NOT NULL,
		publisher TEXT NOT NULL,
		issn TEXT,
		eissn TEXT
	);"""
 
	create_table(conn, journal_table)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def create_jobs_table(conn):
	jobs_table = """CREATE TABLE IF NOT EXISTS jobs (
		id INTEGER PRIMARY KEY,
		journal_id INTEGER NOT NULL,
  		keywords TEXT NOT NULL,
		is_complete BOOLEAN NOT NULL,
		in_progress BOOLEAN NOT NULL,
		current_index INTEGER NOT NULL,
		FOREIGN KEY (journal_id) REFERENCES journal(id)
	);"""
 
	create_table(conn, jobs_table)
 
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def create_results_table(conn):	
	results_table = """CREATE TABLE IF NOT EXISTS results (
		id INTEGER PRIMARY KEY,
		abstract TEXT NOT NULL,
		authors TEXT NOT NULL,
		title TEXT NOT NULL,
		year INTEGER NOT NULL,
		keywords TEXT NOT NULL,
		doi INTEGER NOT NULL,
		journal TEXT NOT NULL
	);"""

	create_table(conn, results_table)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def create_tables(conn):
    create_journal_table(conn)
    create_jobs_table(conn)
    create_results_table(conn)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def populate_journals_table(conn):
	
	journals = load_journals()
	
	for journal in journals:
		insert_journal = """INSERT INTO journal (title, publisher, issn, eissn)
							VALUES (?, ?, ?, ?);"""
		
		conn.execute(insert_journal, (journal['title'], journal['publisher'], journal['issn'], journal['eissn']))
		
	conn.commit()	

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def populate_jobs_table(conn):
    
	keywords = load_keywords()
	
	cursor = conn.cursor()
	cursor.execute("SELECT id FROM journal")
	journal_ids = cursor.fetchall()

	cursor.execute("PRAGMA table_info(jobs)")
	
	for journal_id in journal_ids:
		for keyword in keywords:
			insert_job = """INSERT INTO jobs (keywords, journal_id, is_complete, in_progress, current_index)
							VALUES (?, ?, ?, ?, ?);"""
			conn.execute(insert_job, (keyword, journal_id[0], False, False, 0))

	conn.commit()

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def populate_tables(conn):
	populate_journals_table(conn)	
	populate_jobs_table(conn)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def display_table(	conn,
    				table_name: str) -> None:
	cursor = conn.cursor()
	cursor.execute(f'SELECT * FROM {table_name}')
	rows = cursor.fetchall()

	for row in rows:
		print(row)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def main():
	
	# connect to the database
	db_conn = create_connection()
 
	# create the tables
	create_tables(db_conn)
 
	# populate tables with data
	populate_tables(db_conn)
	 
	# close the connection
	db_conn.close()

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

if __name__ == "__main__":
    main()