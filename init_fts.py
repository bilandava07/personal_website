import sqlite3

def init_fts(db_name):
    '''Initializes the FTS5 table for trips'''
    with sqlite3.connect(db_name) as conn:
        # Create FTS5 virtual table linked to trips table
        conn.execute('''
            CREATE VIRTUAL TABLE IF NOT EXISTS trips_fts USING fts5(
                trip_name,
                trip_description,
                content='trips',
                content_rowid='trip_id'
            )
        ''')

        # Rebuild the FTS index from existing trips
        conn.execute("INSERT INTO trips_fts(trips_fts) VALUES('rebuild');")
        
        conn.commit()