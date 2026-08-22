import gzip
import csv
import json
import urllib.request
import os

basics_url = "https://imdbws.com"
ratings_url = "https://imdbws.com"
output_file = "imdb_index.json"

print("📥 IMDb verileri indiriliyor...")
urllib.request.urlretrieve(basics_url, "basics.tsv.gz")
urllib.request.urlretrieve(ratings_url, "ratings.tsv.gz")

ratings_db = {}
print("⚡ Puanlar hafızaya alınıyor...")
with gzip.open("ratings.tsv.gz", mode="rt", encoding="utf-8") as f:
    reader = csv.reader(f, delimiter="\t")
    next(reader)
    for row in reader:
        ratings_db[row[0]] = (row[1], row[2]) # rating, votes
os.remove("ratings.tsv.gz")

print("⚡ Veriler birleştiriliyor ve JSON formatına yazılıyor...")
# Satır satır yazarak GitHub sunucusunun RAM'ini şişirmiyoruz
with open(output_file, "w", encoding="utf-8") as out:
    out.write("{\n")
    
    with gzip.open("basics.tsv.gz", mode="rt", encoding="utf-8") as f:
        reader = csv.reader(f, delimiter="\t")
        next(reader)
        
        first = True
        for row in reader:
            tconst = row[0]
            # Sadece puanı olan yapımları alarak dosyayı hafifletiyoruz
            if tconst in ratings_db:
                rating, votes = ratings_db[tconst]
                
                movie_data = {
                    "t": row[2],  # primaryTitle
                    "y": row[5] if row[5] != "\\N" else "",  # startYear
                    "g": row[8] if row[8] != "\\N" else "",  # genres
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
