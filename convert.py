import gzip
import csv
import sqlite3
import os
import requests

# ⚡ GitHub Actions IPv6 Bağlantı Yaması
import urllib3.util.connection as urllib3_cn
def allowed_gai_family():
	import socket
	return socket.AF_INET
urllib3_cn.allowed_gai_family = allowed_gai_family

# basics_url = "https://datasets.imdbws.com/title.basics.tsv.gz"
ratings_url = "https://datasets.imdbws.com/title.ratings.tsv.gz"
db_file = "imdb_complete.db"

if os.path.exists(db_file):
	os.remove(db_file)

# 1. Veritabanı Bağlantısı Açılışı
conn = sqlite3.connect(db_file)
cursor = conn.cursor()

# SQLite Hız Optimizasyonları
cursor.execute("PRAGMA synchronous = OFF;")
cursor.execute("PRAGMA journal_mode = MEMORY;")

# Tablo Şablonları
cursor.execute('''
	CREATE TABLE IF NOT EXISTS basics (
		tconst TEXT PRIMARY KEY,
		titleType TEXT,
		primaryTitle TEXT,
		originalTitle TEXT,
		startYear TEXT,
		runtimeMinutes TEXT,
		genres TEXT
	)
''')

cursor.execute('''
	CREATE TABLE IF NOT EXISTS ratings (
		tconst TEXT PRIMARY KEY,
		rating REAL,
		votes INTEGER
	)
''')

def download_file(url, filename):
	print(f"📥 {filename} indiriliyor...")
	with requests.get(url, stream=True, headers={'User-Agent': 'Mozilla/5.0'}) as r:
		r.raise_for_status()
		with open(filename, 'wb') as f:
			for chunk in r.iter_content(chunk_size=8192):
				f.write(chunk)
	print(f"✅ {filename} indirmesi tamamlandı.")

# Dosyaları Sırayla İndir
try:
	# download_file(basics_url, "basics.tsv.gz")
	download_file(ratings_url, "ratings.tsv.gz")
except Exception as e:
	print(f"❌ İndirme hatası: {e}")
	raise

# 2. Reyting Verilerini RAM'e Alma
ratings_db = {}
print("⚡ Puanlar hafızaya alınıyor...")
with gzip.open("ratings.tsv.gz", mode="rt", encoding="utf-8") as f:
	reader = csv.reader(f, delimiter="\t")
	next(reader)
	for row in reader:
		if len(row) >= 3:
			ratings_db[row[0]] = (row[1], row[2])
os.remove("ratings.tsv.gz")
print("✅ Puanlar hafızaya alındı. Geçici ratings dosyası silindi.")

# 3. Basics ve Ratings Verilerini SQL'e Yazma
# print("⚡ Veritabanı oluşturuluyor ve eşleştiriliyor...")
# with gzip.open("basics.tsv.gz", mode="rt", encoding="utf-8") as f:
	# reader = csv.reader(f, delimiter="\t")
	# next(reader)
	# batch_basics = []
	# batch_ratings = []
	
	# for row in reader:
		# if not row or len(row) < 1: 
			# continue
		# tconst = row[0]
		
		# if tconst in ratings_db:
			# rating, votes = ratings_db[tconst]
			
			# title = row[2] if len(row) > 2 else ""
			# orig_title = row[3] if len(row) > 3 else ""
			# year = row[5] if len(row) > 5 else ""
			# runtime = row[7] if len(row) > 7 else ""
			# genres = row[8] if len(row) > 8 else ""
			
			# batch_basics.append((tconst, row[1] if len(row) > 1 else "", title, orig_title, year, runtime, genres))
			# batch_ratings.append((tconst, float(rating), int(votes)))
			
		# if len(batch_basics) == 100000:
			# cursor.executemany("INSERT OR REPLACE INTO basics VALUES (?, ?, ?, ?, ?, ?, ?)", batch_basics)
			# cursor.executemany("INSERT OR REPLACE INTO ratings VALUES (?, ?, ?)", batch_ratings)
			# batch_basics, batch_ratings = [], []
			
	# if batch_basics:
		# cursor.executemany("INSERT OR REPLACE INTO basics VALUES (?, ?, ?, ?, ?, ?, ?)", batch_basics)
		# cursor.executemany("INSERT OR REPLACE INTO ratings VALUES (?, ?, ?)", batch_ratings)

# os.remove("basics.tsv.gz")
# print("✅ Temel veriler SQL tablolarına başarıyla basıldı. Geçici basics dosyası silindi.")

# 4. Hızlı Arama İndekslerinin Oluşturulması (Bağlantı Açıkken Yapılır)
print("⚡ Arama hızlandırma indeksleri oluşturuluyor...")
# cursor.execute("CREATE INDEX IF NOT EXISTS idx_basics_tconst ON basics(tconst);")
cursor.execute("CREATE INDEX IF NOT EXISTS idx_ratings_tconst ON ratings(tconst);")
# cursor.execute("CREATE INDEX IF NOT EXISTS idx_basics_title ON basics(primaryTitle);")
# cursor.execute("CREATE INDEX IF NOT EXISTS idx_basics_orig_title ON basics(originalTitle);")

# 5. Kapatma ve Kilitleme İşlemleri
conn.commit()
conn.close()
print("✅ SQLite veritabanı isim indeksleriyle birlikte başarıyla tamamlandı!")
