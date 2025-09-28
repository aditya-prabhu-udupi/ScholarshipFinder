import sqlite3




def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    # Scholarships table
    c.execute('''
        CREATE TABLE IF NOT EXISTS scholarships (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            eligibility TEXT,
            amount TEXT,
            deadline TEXT,
            category TEXT,
            link TEXT,
            source TEXT,
            approved INTEGER DEFAULT 1
        )
    ''')

    # Internships table
    c.execute('''
        CREATE TABLE IF NOT EXISTS internships (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            company TEXT,
            description TEXT,
            eligibility TEXT,
            location TEXT,
            stipend TEXT,
            duration TEXT,
            deadline TEXT,
            link TEXT,
            source TEXT,
            approved INTEGER DEFAULT 1
        )
    ''')

    # Subscribers table
    c.execute('''
        CREATE TABLE IF NOT EXISTS subscribers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL UNIQUE
        )
    ''')

    conn.commit()
    conn.close()


def insert_sample_data():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    # Scholarships
    c.execute("SELECT COUNT(*) FROM scholarships")
    if c.fetchone()[0] == 0:
        for s in sample_scholarships:
            c.execute('''
                INSERT INTO scholarships (
                    title, description, eligibility, amount, deadline, category, link, source
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', s)

    # Internships
    c.execute("SELECT COUNT(*) FROM internships")
    if c.fetchone()[0] == 0:
        for i in sample_internships:
            c.execute('''
                INSERT INTO internships (
                    title, company, description, eligibility, location, stipend, duration, deadline, link, source
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', i)

    conn.commit()
    conn.close()


if __name__ == "__main__":
    init_db()
    insert_sample_data()
    print("✅ Database initialized with scholarships, internships, and subscribers.")
