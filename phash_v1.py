# python3.12 -m venv venv
# source venv/bin/activate
# pip install imagehash pillow pillow-heif gphotospy

import os
import datetime
from PIL import Image
import imagehash
from pillow_heif import register_heif_opener

import sqlite3

from gphotospy import authorize, media
from gphotospy.album import Album
from gphotospy.media import Media, date_range, date, MEDIAFILTER
from concurrent.futures import ThreadPoolExecutor

import requests

register_heif_opener()

CLIENT_SECRET_FILE = "credentials.json"

conn = None
cursor = None

def calculate_phash(photo_path):
    img = Image.open(photo_path)
    photo_hash = imagehash.phash(img)
    return photo_hash

def get_local_image_data(photo_path):
    photo_hash = calculate_phash(photo_path)
    photo_time = os.path.getmtime(photo_path)
    return {"photo_path": photo_path,
            "photo_phash": photo_hash,
            "photo_time": photo_time}
    
if __name__ == '__main__':
    folder_path = 'img'
    
    # Database initialization
    conn = sqlite3.connect('google_photos_cache.sqlite')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Create Google Photos data table if not exists
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS google_photos_data (
            photo_id TEXT PRIMARY KEY,
            phash TEXT,
            productUrl TEXT,
            baseUrl TEXT,
            mimeType TEXT,
            creationTime TEXT,
            width INT,
            height INT,
            cameraModel INT,
            filename TEXT
        )
    ''')

    conn.commit()

    local_images = [get_local_image_data(os.path.join(folder_path, filename)) for filename in os.listdir(folder_path) if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.heic'))]

    service = authorize.init(CLIENT_SECRET_FILE)
    media_manager = Media(service)
    
    for local_image in local_images:
        # saearch hash in DB

        print(f"Searching Google photos for {os.path.basename(local_image["photo_path"])}: {local_image["photo_phash"]}")

        from_date = date(2020,1,1)
        end_date_dtobj = datetime.datetime.fromtimestamp(local_image["photo_time"], datetime.UTC)
        end_date = date(end_date_dtobj.year, end_date_dtobj.month, end_date_dtobj.day)
        
        media_iterator = media_manager.search([date_range(from_date, end_date), MEDIAFILTER.PHOTO])
        
        for current_media in media_iterator:
            current_phash = None
            # check if it was taekn after our image

            # check if in DB
            cursor.execute("SELECT phash FROM google_photos_data WHERE photo_id = ?", (current_media["id"],))
            current_phash = cursor.fetchone()
            if (current_phash):
                current_phash = dict(current_phash)
                current_phash = current_phash.get("phash", None)
                if (current_phash):
                    current_phash = imagehash.hex_to_hash(current_phash)
                print ("In DB")

            if (not current_phash):
                print ("Calculating pHash")
                current_phash = calculate_phash(requests.get(current_media["baseUrl"], stream=True).raw)

            # insret to db
            cursor.execute('''
                    INSERT OR REPLACE INTO google_photos_data 
                    (photo_id, phash, productUrl, baseUrl, mimeType, creationTime, width, height, cameraModel, filename)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (current_media["id"], str(current_phash), current_media["productUrl"], current_media["baseUrl"], current_media["mimeType"], current_media["mediaMetadata"]["creationTime"], current_media["mediaMetadata"]["width"], current_media["mediaMetadata"]["height"], current_media["mediaMetadata"]["photo"].get("cameraModel", False), current_media["filename"]))
            conn.commit()

            # print(f"""{current_media["id"]} {current_phash} {current_phash - local_image["photo_phash"]}""")
                            # """productUrl:     {current_media["productUrl"]}
                            # baseUrl:        {current_media["baseUrl"]}
                            # mimeType:       {current_media["mimeType"]}
                            # creationTime:   {current_media["mediaMetadata"]["creationTime"]}
                            # width:          {current_media["mediaMetadata"]["width"]}
                            # height:         {current_media["mediaMetadata"]["height"]}
                            # filename:       {current_media["filename"]}"""
            
            if current_phash - local_image["photo_phash"] < 5:
                print(f"""Match found for {os.path.basename(local_image["photo_path"])}: Google Photo ID {current_media["id"]}
productUrl:     {current_media["productUrl"]}
                            """)
                # check if it has camera model
                if current_media["mediaMetadata"]["photo"].get("cameraModel", False):
                    break

            current_media["id"]
            current_media["productUrl"]
            current_media["baseUrl"]
            current_media["mimeType"]
            current_media["mediaMetadata"]["creationTime"]
            current_media["mediaMetadata"]["width"]
            current_media["mediaMetadata"]["height"]
            # current_media["mediaMetadata"]["photo"]["cameraModel"]
            current_media["filename"]
    conn.close()