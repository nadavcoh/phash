import psycopg2
from PIL import Image
import imagehash
import json

maxDifference = 20 #the maximum hamming distance
fileName = "imageToSearch.jpg" #image can be any file type accepted by PIL

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

def twos_complement(hexstr, bits):
    value = int(hexstr,16) #convert hexadecimal to integer

    #convert from unsigned number to signed number with "bits" bits
    if value & (1 << (bits-1)):
        value -= 1 << bits
    return value
        
img = Image.open(fileName)
imgHash = str(imagehash.phash(img))
hashInt = twos_complement(imgHash, 64) #convert from hexadecimal to 64 bit signed integer
print(hashInt)
cursor.execute("SELECT url FROM hashes WHERE hash <@ (%s, %s)",(hashInt, maxDifference))
hashRows = cursor.fetchall()
print(hashRows)