# python3.12 -m venv venv
# source venv/bin/activate
# pip install imagehash pillow pillow-heif gphotospy

import os
from PIL import Image
import imagehash
import sqlite3
from gphotospy import authorize
from gphotospy.album import Album
from gphotospy.media import Media
from concurrent.futures import ThreadPoolExecutor
from pillow_heif import register_heif_opener
import requests

register_heif_opener()

CLIENT_SECRET_FILE = "credentials.json"

# Database initialization
def initialize_database():
    conn = sqlite3.connect('google_photos_cache.sqlite')
    cursor = conn.cursor()

    # Create Google Photos data table if not exists
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS google_photos_data (
            photo_id TEXT PRIMARY KEY,
            hash TEXT,
            resolution_width INTEGER,
            resolution_height INTEGER,
            has_exif INTEGER,
            timestamp INTEGER
        )
    ''')

    conn.commit()
    conn.close()

# Google Photos authentication
def authenticate_google_photos():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json')

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return creds

def calculate_phash(photo_url):
    img = Image.open(photo_url)
    photo_hash = imagehash.phash(img)
    return photo_hash

# Function to calculate pHash and resolution
def calculate_phash_and_resolution(item):
    photo_id = item['id']
    photo_url = item['baseUrl'] + '=w100-h100'
    resolution = item['size']

    photo_hash = calculate_phash(photo_url)

    return photo_id, {'hash': photo_hash, 'resolution': resolution, 'has_exif': 'exif' in img.info}

# Function to store Google Photos data in the database
def store_google_photos_data(google_photos_data):
    conn = sqlite3.connect('google_photos_cache.db')
    cursor = conn.cursor()

    for photo_id, data in google_photos_data.items():
        hash_value = data['hash']
        resolution_width, resolution_height = data['resolution']
        has_exif = 1 if data.get('has_exif', False) else 0

        cursor.execute('''
            INSERT OR REPLACE INTO google_photos_data 
            (photo_id, hash, resolution_width, resolution_height, has_exif)
            VALUES (?, ?, ?, ?, ?)
        ''', (photo_id, hash_value, resolution_width, resolution_height, has_exif))

    conn.commit()
    conn.close()

# Function to load Google Photos data from the database
# def load_google_photos_data():
#     conn = sqlite3.connect('google_photos_cache.db')
#     cursor = conn.cursor()

#     cursor.execute('SELECT * FROM google_photos_data')
#     rows = cursor.fetchall()

#     google_photos_data = {}
#     for row in rows:
#         photo_id, hash_value, resolution_width, resolution_height, has_exif = row
#         google_photos_data[photo_id] = {
#             'hash': hash_value,
#             'resolution': (resolution_width, resolution_height),
#             'has_exif': bool(has_exif)
#         }

#     conn.close()
#     return google_photos_data

# Function to compare a local image to Google Photos data
def compare_image_to_google_photos(local_image):
    local_image_path, local_image_hash = local_image

    # local_creation_time = get_image_creation_time(local_image_path)
    for hash in local_image:
        if 'hash' not in google_photo_data:
            google_photo_id, google_photo_data = calculate_phash_and_resolution(photo_data)
            google_photos_data[google_photo_id] = google_photo_data
            store_google_photos_data({google_photo_id: google_photo_data})

        google_photo_hash = google_photo_data['hash']
        google_resolution = google_photo_data['resolution']
        google_creation_time = get_google_photo_creation_time(photo_id)

        if local_image_hash == google_photo_hash:
            print(f'Match found for {os.path.basename(local_image_path)}: Google Photo ID {photo_id}')
            return photo_id

        # if google_photo_data.get('has_exif', False)
    return None

# Other utility functions (get_image_resolution, get_image_creation_time, get_google_photo_creation_time, create_album)...

if __name__ == '__main__':
    folder_path = 'img'

    initialize_database()

    local_images = [(os.path.join(folder_path, filename), calculate_phash(os.path.join(folder_path, filename))) for filename in os.listdir(folder_path) if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.heic'))]

    service = authorize.init(CLIENT_SECRET_FILE)
    media_manager = Media(service)
    
    for local_image_path, local_image_phash in local_images:
        # saearch hash in DB
        print(f"Searching Google photos for {os.path.basename(local_image_path)}: {local_image_phash}")
        media_iterator = media_manager.list()
        for media in media_iterator:
            # check if it was taekn after our image
                # check if not in DB
                    # insret to db
            # else continue to compare
                # if media in DB
                    # if DB has hash
                        # fetch hash
                    # else in DB without hash
                        # calculate hash
                        # push to DB
                # else not in DB
                    # calculate hash
                    # insert to DB
            
            media["phash"] = calculate_phash(requests.get(media["baseUrl"], stream=True).raw)

            print(f"""{media["id"]} {media["phash"]} {media["phash"] - local_image_phash}""")
                            # """productUrl:     {media["productUrl"]}
                            # baseUrl:        {media["baseUrl"]}
                            # mimeType:       {media["mimeType"]}
                            # creationTime:   {media["mediaMetadata"]["creationTime"]}
                            # width:          {media["mediaMetadata"]["width"]}
                            # height:         {media["mediaMetadata"]["height"]}
                            # filename:       {media["filename"]}"""
            
            if media["phash"] - local_image_phash < 5:
                print(f"""Match found for {os.path.basename(local_image_path)}: Google Photo ID {media["id"]}
                            productUrl:     {media["productUrl"]}
                            baseUrl:        {media["baseUrl"]}
                            mimeType:       {media["mimeType"]}
                            creationTime:   {media["mediaMetadata"]["creationTime"]}
                            width:          {media["mediaMetadata"]["width"]}
                            height:         {media["mediaMetadata"]["height"]}
                            cameraModel:    {media["mediaMetadata"]["photo"].get("cameraModel", False)}
                            filename:       {media["filename"]}""")
                # check if it has camera model
                if media["mediaMetadata"]["photo"].get("cameraModel", False):
                    break

            media["id"]
            media["productUrl"]
            media["baseUrl"]
            media["mimeType"]
            media["mediaMetadata"]["creationTime"]
            media["mediaMetadata"]["width"]
            media["mediaMetadata"]["height"]
            # media["mediaMetadata"]["photo"]["cameraModel"]
            media["filename"]