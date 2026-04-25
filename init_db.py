import sqlite3

conn = sqlite3.connect('blood_bank.db')
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS donor (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    age INTEGER,
    gender TEXT,
    blood_group TEXT,
    phone TEXT,
    city TEXT
);
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS donation (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    donor_id INTEGER,
    date TEXT,
    FOREIGN KEY(donor_id) REFERENCES donor(id)
);
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS stock (
    blood_group TEXT PRIMARY KEY,
    units INTEGER DEFAULT 0
);
""")

# Seed stock rows if missing
groups = ['A+','A-','B+','B-','O+','O-','AB+','AB-']
for g in groups:
    cursor.execute("INSERT OR IGNORE INTO stock (blood_group, units) VALUES (?, ?)", (g, 0))

conn.commit()
conn.close()
print("Database initialized successfully.")
