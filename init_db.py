import sqlite3

conn = sqlite3.connect('scholarships.db')
c = conn.cursor()

# =====================
# Create main tables
# =====================
c.execute('''
    CREATE TABLE IF NOT EXISTS scholarships (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        provider TEXT,
        eligibility TEXT,
        amount TEXT,
        deadline TEXT,
        link TEXT,
        approved INTEGER DEFAULT 0
    )
''')

c.execute('''
    CREATE TABLE IF NOT EXISTS internships (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        provider TEXT,
        eligibility TEXT,
        amount TEXT,
        deadline TEXT,
        link TEXT,
        duration TEXT,      
        location TEXT, 
        approved INTEGER DEFAULT 0
    )
''')

c.execute('''
    CREATE TABLE IF NOT EXISTS subscribers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL
    )
''')

# =====================
# Create archive tables
# =====================
c.execute('''
    CREATE TABLE IF NOT EXISTS scholarships_archive (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        provider TEXT,
        eligibility TEXT,
        amount TEXT,
        deadline TEXT,
        link TEXT,
        approved INTEGER DEFAULT 0
    )
''')

c.execute('''
    CREATE TABLE IF NOT EXISTS internships_archive (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        provider TEXT,
        eligibility TEXT,
        amount TEXT,
        deadline TEXT,
        link TEXT,
        duration TEXT,     
        location TEXT,      
        approved INTEGER DEFAULT 0
    )
''')


# Insert scholarships
c.execute("SELECT COUNT(*) FROM scholarships")
if c.fetchone()[0] == 0:
    c.executemany('''
        INSERT INTO scholarships (name, provider, eligibility, amount, deadline, link, approved)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', sample_scholarships)

# Insert internships
c.execute("SELECT COUNT(*) FROM internships")
if c.fetchone()[0] == 0:
    c.executemany('''
    INSERT INTO internships 
    (name, provider, eligibility, amount, deadline, link, duration, location, approved)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''', sample_internships)


conn.commit()
conn.close()

print("✅ Database initialized and tables created.")
