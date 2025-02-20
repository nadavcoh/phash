from seleniumbase import SB
from selenium.webdriver.common.keys import Keys
from time import sleep

import psycopg2
import psycopg2.extras  # Import extras module
import os
from PIL import Image
from pillow_heif import register_heif_opener
import imagehash
import json
import zipfile
import time
import argparse
from datetime import datetime
import pytz
import msvcrt
#from videohash import VideoHash

register_heif_opener()

def twos_complement(hexstr, bits):
    value = int(hexstr,16) #convert hexadecimal to integer

    #convert from unsigned number to signed number with "bits" bits
    if value & (1 << (bits-1)):
        value -= 1 << bits
    return value

def is_file_in_use(filepath):
    try:
        os.rename(filepath, filepath)
        return False
    except OSError:
        return True

def get_start_url(option):
    with open('config.json') as config_file:
        config = json.load(config_file)

    conn = psycopg2.connect(
        database=config["DB_NAME"],
        user=config["DB_USER"],
        password=config["DB_PASSWORD"],
        host=config["DB_HOST"]
    )
    
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    print("Connection Successful to PostgreSQL")
    cursor.execute("SET TIME ZONE 'Asia/Jerusalem';")

    if option == "last":
        cursor.execute("SELECT url FROM hashes ORDER BY id DESC LIMIT 1")
    elif option == "oldest":
        cursor.execute("SELECT url FROM hashes ORDER BY timestamp ASC, id DESC LIMIT 1")
    else:
        return None

    record = cursor.fetchone()
    cursor.close()
    conn.close()

    return record['url'] if record else None

def my_sb(sb=None, start=None):
    context = None
    if not sb:
        context = SB(uc=True)
        sb = context.__enter__()

    sb.open("https://photos.google.com/login")
    # Wait for the user to complete all authentication steps
    input("Press Enter after completing authentication...")
    
    if start is None:
        sb.send_keys("html", Keys.ARROW_RIGHT)
        sb.send_keys("html", Keys.ENTER)
    else:
        sb.open(start)
    sb.send_keys("html", "i")
    
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
    cursor.execute("SET TIME ZONE 'Asia/Jerusalem';")
    i=0
    flag = True
    while flag:
        print (i)
        sleep(5)
        url = sb.get_current_url()
        
        cursor.execute("SELECT 1 FROM hashes WHERE url = %s", (url,))
        if cursor.fetchone():
            print("URL already exists in the database.")
        else:
            preview_elements = sb.find_elements("img[aria-label^='Photo']")
            displayed_preview_elements = [x for x in preview_elements if x.is_displayed()]
            if not displayed_preview_elements:
                print("No image to process.")
            else:
                preview_element = displayed_preview_elements[0]
                preview_url = preview_element.get_attribute('src')
                label = preview_element.get_attribute('aria-label')
                # sample label = "Photo – Portrait – 16 Nov 2024, 10:28:33"

                filename_elements = sb.find_elements("div[aria-label^='Filename']")
                filename_element = [x for x in filename_elements if x.is_displayed()][0]
                filename = filename_element.text
                
                size_elements = sb.find_elements("span[aria-label^='Size:']")
                size_element = [x for x in size_elements if x.is_displayed()][0]
                size = size_element.text

                filesize_elements = sb.find_elements("span[aria-label^='File size:']")
                displayed_filesize_elements = [x for x in filesize_elements if x.is_displayed()]
                if displayed_filesize_elements:
                    filesize_element = displayed_filesize_elements[0]
                    filesize = filesize_element.text
                else:
                    filesize = None
                    print("No file size found.")

                camera_elements = sb.find_elements("div[aria-label^='Camera name:']")
                displayed_camera_elements = [x for x in camera_elements if x.is_displayed()]
                if displayed_camera_elements:
                    camera_element = displayed_camera_elements[0]
                    camera_name = camera_element.text
                else:
                    camera_name = None
                    print("No camera name found.")

                aperture_elements = sb.find_elements("span[aria-label^='Aperture:']")
                displayed_aperture_elements = [x for x in aperture_elements if x.is_displayed()]
                if displayed_aperture_elements:
                    aperture_element = displayed_aperture_elements[0]
                    aperture = aperture_element.text
                else:
                    aperture = None
                    print("No aperture found.")

                exposure_elements = sb.find_elements("span[aria-label^='Exposure time:']")
                displayed_exposure_elements = [x for x in exposure_elements if x.is_displayed()]
                if displayed_exposure_elements:
                    exposure_element = displayed_exposure_elements[0]
                    exposure = exposure_element.text
                else:
                    exposure = None
                    print("No exposure time found.")

                focal_length_elements = sb.find_elements("span[aria-label^='Focal length:']")
                displayed_focal_length_elements = [x for x in focal_length_elements if x.is_displayed()]
                if displayed_focal_length_elements:
                    focal_length_element = displayed_focal_length_elements[0]
                    focal_length = focal_length_element.text
                else:
                    focal_length = None
                    print("No focal length found.")
                
                location_elements = sb.find_elements("a[title='Show location of photo on Google Maps']")
                displayed_location_elements = [x for x in location_elements if x.is_displayed()]
                if displayed_location_elements:
                    location_element = displayed_location_elements[0]
                    location = location_element.get_attribute('href')
                else:
                    location = None
                    print("No location found.")
            
                location_name_elements = sb.find_elements("div[aria-label='Edit location']")
                displayed_location_name_elements = [x for x in location_name_elements if x.is_displayed()]
                if displayed_location_name_elements:
                    location_name_element = displayed_location_name_elements[0]
                    location_name = location_name_element.text
                else:
                    location_name = None
                    print("No location name found.")

                timezone_elements = sb.find_elements("span[aria-label^='GMT']")
                displayed_timezone_elements = [x for x in timezone_elements if x.is_displayed()]
                if displayed_timezone_elements:
                    timezone_element = displayed_timezone_elements[0]
                    timezone = timezone_element.text
                else:
                    timezone = None
                    print("No timezone found.")
                # sample timezone = "GMT+02:00"

                sb.send_keys("html", Keys.SHIFT + "d")
                sleep(6)
                               
                download_path = sb.get_downloads_folder()

                while not os.path.isfile(os.path.join(download_path, filename)):
                    latest_file = max([os.path.join(download_path, f) for f in os.listdir(download_path)], key=os.path.getctime)
                    while latest_file.endswith('.crdownload'):
                        sleep(1)
                        latest_file = max([os.path.join(download_path, f) for f in os.listdir(download_path)], key=os.path.getctime)
                    
                if latest_file.endswith('.zip'):
                    if os.path.getsize(latest_file) == 0:
                        input(f"Empty zip file. Press Enter to continue...\n{latest_file}")
                    with zipfile.ZipFile(latest_file, 'r') as zip_ref:
                        zip_ref.extractall(download_path)
                    while is_file_in_use(latest_file):
                        time.sleep(1)
                    os.remove(latest_file)
                    latest_file = max([os.path.join(download_path, f) for f in os.listdir(download_path)], key=os.path.getctime)
                if latest_file.endswith('.mov'):
                    while is_file_in_use(latest_file):
                        time.sleep(1)
                    os.remove(latest_file)
                    latest_file = max([os.path.join(download_path, f) for f in os.listdir(download_path)], key=os.path.getctime)
                if os.path.getsize(latest_file) == 0:
                    input(f"Empty file. Press Enter to continue...\n{latest_file}")
                img = Image.open(latest_file)
                imgHash = str(imagehash.phash(img))
                img.close()
                hashInt = twos_complement(imgHash, 64) #convert from hexadecimal to 64 bit signed integer

                while is_file_in_use(latest_file):
                    time.sleep(1)
                    print("file in use")
                os.remove(latest_file)
                
                latest_file = max([os.path.join(download_path, f) for f in os.listdir(download_path)], key=os.path.getctime)
                if latest_file.endswith('.mov'):
                    while is_file_in_use(latest_file):
                        time.sleep(1)
                    os.remove(latest_file)

                label_parts = label.split(' – ')
                date_str = label_parts[-1]
                timestamp = date_str + timezone[3:]

                cursor.execute(
                    "INSERT INTO hashes(hash, url, preview_url, label, filename, size, filesize, camera_name, aperture, exposure, focal_length, location, location_name, timezone, timestamp) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                    (hashInt, url, preview_url, label, filename, size, filesize, camera_name, aperture, exposure, focal_length, location, location_name, timezone, timestamp)
                )
                conn.commit()
                print(f"added image to database")
                # print(url, preview_url, label, filename, size, filesize)
        sb.send_keys("html", Keys.ARROW_RIGHT)
        i+=1
        if msvcrt.kbhit():
            if msvcrt.getch() == b'q':
                flag = False

    return context, sb, conn, cursor

def fetch_and_print_records():
    with open('config.json') as config_file:
        config = json.load(config_file)

    conn = psycopg2.connect(
        database=config["DB_NAME"],
        user=config["DB_USER"],
        password=config["DB_PASSWORD"],
        host=config["DB_HOST"]
    )
    
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    print("Connection Successful to PostgreSQL")
    cursor.execute("SET TIME ZONE 'Asia/Jerusalem';")
    # Fetch the record with the highest ID
    cursor.execute("SELECT id, timestamp, url FROM hashes ORDER BY id DESC LIMIT 1")
    highest_id_record = cursor.fetchone()
    print(f"Record with highest ID: ID = {highest_id_record['id']}, Timestamp = {highest_id_record['timestamp']}, URL = {highest_id_record['url']}")

    # Fetch the record with the oldest timestamp
    cursor.execute("SELECT id, timestamp, url FROM hashes ORDER BY timestamp ASC, id DESC LIMIT 1")
    oldest_timestamp_record = cursor.fetchone()
    print(f"Record with oldest timestamp: ID = {oldest_timestamp_record['id']}, Timestamp = {oldest_timestamp_record['timestamp']}, URL = {oldest_timestamp_record['url']}")

    cursor.close()
    conn.close()

def main():
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--start', type=str, default=None, help='a URL for the start value or "oldest" or "last"')
    parser.add_argument('--fetch-records', action='store_true', help='fetch and print records from the database')
    args = parser.parse_args()

    if args.fetch_records:
        fetch_and_print_records()
    else:
        start = args.start
        if start in ["oldest", "last"]:
            start = get_start_url(start)
        # Pass the start argument to my_sb
        with SB(uc=True) as sb:
            context, sb, conn, cursor = my_sb(sb, start)

if __name__ == "__main__":
    main()