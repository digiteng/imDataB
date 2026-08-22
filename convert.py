import sqlite3
import urllib.request
import gzip
import csv
import os

db_file = "imdb_complete.db"
basics_url = "https://imdbws.com"
ratings_url = "https://imdbws.com"

# Eski db varsa temizle
if os.path.exists(db_file):
	os.remove(db_file)

conn = sqlite3.connect(db_file)
cursor = conn.cursor()

# SQLite Performans Ayarları
cursor.execute("PRAGMA synchronous = OFF;")
cursor.execute("PRAGMA journal_mode = MEMORY;")

# Tablo Yapıları
cursor.execute('''
	CREATE TABLE basics (
		tconst TEXT PRIMARY KEY,
		titleType TEXT,
		primaryTitle TEXT,
		originalTitle TEXT,
		isAdult INTEGER,
		startYear TEXT,
		endYear TEXT,
		runtimeMinutes TEXT,
		genres TEXT
	)
''')

cursor.execute('''
	CREATE TABLE ratings (
		tconst TEXT PRIMARY KEY,
		rating REAL,
		votes INTEGER
	)
''')

def safe_row_generator(f_in):
	# gzip dosyasını doğrudan text modunda sarmala
	f_text = gzip.open(f_in, mode="rt", encoding="utf-8")
	reader = csv.reader(f_text, delimiter="\t")
	next(reader) # Başlığı atla
	for row in reader:
		clean_row = row[:9]
		while len(clean_row) < 9:
			clean_row.append(None)
		yield clean_row

print("📥 1/2: title.basics.tsv.gz indiriliyor ve işleniyor...")
urllib.request.urlretrieve(basics_url, "basics.tsv.gz")
batch = []
for row in safe_row_generator("basics.tsv.gz"):
	batch.append(row)
	if len(batch) == 100000:
		cursor.executemany("INSERT OR REPLACE INTO basics VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", batch)
		batch = []
if batch:
	cursor.executemany("INSERT OR REPLACE INTO basics VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", batch)
os.remove("basics.tsv.gz")

print("📥 2/2: title.ratings.tsv.gz indiriliyor ve işleniyor...")
urllib.request.urlretrieve(ratings_url, "ratings.tsv.gz")
f_text_r = gzip.open("ratings.tsv.gz", mode="rt", encoding="utf-8")
reader_r = csv.reader(f_text_r, delimiter="\t")
next(reader_r)

batch = []
for row in reader_r:
	batch.append((row[0], float(row[1]), int(row[2])))
	if len(batch) == 100000:
		cursor.executemany("INSERT OR REPLACE INTO ratings VALUES (?, ?, ?)", batch)
		batch = []
if batch:
	cursor.executemany("INSERT OR REPLACE INTO ratings VALUES (?, ?, ?)", batch)
os.remove("ratings.tsv.gz")

conn.commit()
conn.close()
print("✅ Veritabanı başarıyla hazırlandı!")
