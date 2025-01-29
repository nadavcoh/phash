import psycopg2
import os
from io import BytesIO
from PIL import Image
import imagehash
import json

def twos_complement(hexstr, bits):
        value = int(hexstr,16) #convert hexadecimal to integer

		#convert from unsigned number to signed number with "bits" bits
        if value & (1 << (bits-1)):
            value -= 1 << bits
        return value

with open('config.json') as config_file:
    config = json.load(config_file)

conn = psycopg2.connect(
    database=config["DB_NAME"],
    user=config["DB_USER"],
    password=config["DB_PASSWORD"],
    host=config["DB_HOST"]
)

cursor = conn.cursor()
print("Connection Successful to PostgreSQL")

with open("example.json") as f:
    data = json.load(f)
# img = Image.open(imageBinary)
# imgHash = str(imagehash.dhash(img))
# hashInt = twos_complement(imgHash, 64) #convert from hexadecimal to 64 bit signed integer
cursor.execute("INSERT INTO hashes(hash, url) VALUES (%s, %s)", (1, data["url"],))
conn.commit()
print(f"added image to database")