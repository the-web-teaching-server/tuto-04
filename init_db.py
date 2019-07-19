import sqlite3

conn = sqlite3.connect('.data/shortcuts.db')
cur = conn.cursor()

cur.execute('DROP TABLE IF EXISTS shortcuts')

cur.execute('''
CREATE TABLE shortcuts
(key TEXT PRIMARY KEY, url TEXT)''')

print("Table created!")

cur.execute('INSERT INTO shortcuts VALUES (?, ?), (?, ?) ', 
            ('EbA356Ak', "http://www.example.com", 'aoM4apKh', "http://www.mozilla.org")
)

conn.commit()


cur.execute("SELECT key, url FROM shortcuts")

print("Fake data inserted:")
for key, url in cur.fetchall():
  print(key, "->", url)

conn.close()
