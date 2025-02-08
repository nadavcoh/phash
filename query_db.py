import csv
import psycopg2
from PIL import Image
import imagehash
import json
import os

maxDifference = 3 #the maximum hamming distance

folder_path = 'img'

with open('config.json') as config_file:
    config = json.load(config_file)



def twos_complement(hexstr, bits):
    value = int(hexstr,16) #convert hexadecimal to integer

    #convert from unsigned number to signed number with "bits" bits
    if value & (1 << (bits-1)):
        value -= 1 << bits
    return value

# Function to calculate the phash of an image
def calculate_phash(img):
    imgHash = str(imagehash.phash(img))
    hashInt = twos_complement(imgHash, 64) #convert from hexadecimal to 64 bit signed integer
    return str(hashInt)

conn = psycopg2.connect(
    database=config["DB_NAME"],
    user=config["DB_USER"],
    password=config["DB_PASSWORD"],
    host=config["DB_HOST"]
)

def query_database(hashInt):
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM hashes WHERE hash <@ (%s, %s)",(hashInt, maxDifference))
    results = cursor.fetchall()
    column_names = [desc[0] for desc in cursor.description]

    return column_names, results

def hamming_distance(phash1, phash2):
    """Calculate the Hamming distance between two hashes."""
    return bin(phash1 ^ phash2).count('1')

def calculate_distance(row, hash):
    """Calculate the distance between the calculated phash and the hash from the DB."""
    calculated_phash = int(hash)  # Replace with the actual key for calculated phash
    db_phash = int(row[1])  # Replace with the actual key for DB phash
    return hamming_distance(calculated_phash, db_phash)

cursor = conn.cursor()
print("Connection Successful to PostgreSQL")

csv_file = open('hash_rows.csv', mode='w', newline='')
csv_writer = csv.writer(csv_file)

for filename in os.listdir(folder_path):
    filePath = os.path.join(folder_path, filename)
    img = Image.open(filePath)
    phash = calculate_phash(img)
    columns, rows = query_database(phash)
    csv_writer.writerow([filename])
    columns.append('Distance')
    csv_writer.writerow(columns)
    for row in rows:
        row_list = list(row)  # Convert tuple to list
        row_list.append(calculate_distance(row, phash))
        csv_writer.writerow(row_list)

csv_file.close()