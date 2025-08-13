import sqlite3

# Connect to the database
conn = sqlite3.connect('my_database.db')
cursor = conn.cursor()

# Create a table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS job_applications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company TEXT NOT NULL,
        description TEXT NOT NULL,
        link TEXT NOT NULL,
        CV_path TEXT,
        cover_letter_path TEXT,
        deadline TEXT,
        status INTEGER
        
    )
''')

# Insert a user
cursor.execute("INSERT INTO users (name, age) VALUES (?, ?)", ('Alice', 30))
conn.commit()

# Fetch all users
cursor.execute("SELECT * FROM users")
for user in cursor.fetchall():
    print(user)

# Close connection
conn.close()
