import gzip
import csv
import json
import os
import requests

# ⚡ GİTHUB ACTIONS IPv6 BAĞLANTI HATASINI ÇÖZEN KRİTİK YAMA (Sadece IPv4 Zorlar)
import urllib3.util.connection as urllib3_cn
def allowed_gai_family():
    import socket
    return socket.AF_INET # Sadece IPv4 aktiftir, IPv6'yı tamamen kapatır
urllib3_cn.allowed_gai_family = allowed_gai_family

basics_url = "https://datasets.imdbws.com/title.basics.tsv.gz"
ratings_url = "https://imdbws.com"
output_file = "imdb_index.json"

def download_file(url, filename):
    print(f"📥 {filename} indiriliyor...")
    with requests.get(url, stream=True, headers={'User-Agent': 'Mozilla/5.0'}) as r:
        r.raise_for_status()
        with open(filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)

try:
    download_file(basics_url, "basics.tsv.gz")
    download_file(ratings_url, "ratings.tsv.gz")
except Exception as e:
    print(f"❌ İndirme sırasında hata oluştu: {e}")
    raise

ratings_db = {}
print("⚡ Puanlar hafızaya alınıyor...")
with gzip.open("ratings.tsv.gz", mode="rt", encoding="utf-8") as f:
    reader = csv.reader(f, delimiter="\t")
    next(reader)
    for row in reader:
        ratings_db[row] = (row, row)
os.remove("ratings.tsv.gz")

print("⚡ Veriler birleştiriliyor ve JSON formatına yazılıyor...")
with open(output_file, "w", encoding="utf-8") as out:
    out.write("{\n")
    
    with gzip.open("basics.tsv.gz", mode="rt", encoding="utf-8") as f:
        reader = csv.reader(f, delimiter="\t")
        next(reader)
        
        first = True
        for row in reader:
            tconst = row
            if tconst in ratings_db:
                rating, votes = ratings_db[tconst]
                
                movie_data = {
                    "t": row,
                    "y": row if row != "\\N" else "",
                    "g": row if row != "\\N" else "",
                    "r": rating,
                    "v": votes
                }
                
                if not first:
                    out.write(",\n")
                out.write(f'  "{tconst}": {json.dumps(movie_data, ensure_ascii=False)}')
                first = False
                
    out.write("\n}")

os.remove("basics.tsv.gz")
print("✅ GitHub için optimize edilmiş IMDb JSON İndeksi başarıyla üretildi!")
