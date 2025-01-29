from seleniumbase import SB
from selenium.webdriver.common.keys import Keys
from time import sleep

import psycopg2
import os
from io import BytesIO
from PIL import Image
import imagehash
import json
import urllib.parse

def twos_complement(hexstr, bits):
        value = int(hexstr,16) #convert hexadecimal to integer

		#convert from unsigned number to signed number with "bits" bits
        if value & (1 << (bits-1)):
            value -= 1 << bits
        return value

def my_sb():
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

    context = SB(uc=True)
    sb = context.__enter__()

    sb.open("https://photos.google.com/login")
    # Wait for the user to complete all authentication steps
    input("Press Enter after completing authentication...")
    
    sb.send_keys("html", Keys.ARROW_RIGHT)
    sb.send_keys("html", Keys.ENTER)
    sb.send_keys("html", "i")
    
    sleep(5)
    
    url = sb.get_current_url()
    
    preview_elements = sb.find_elements("img[aria-label^='Photo']")
    preview_element = [x for x in preview_elements if x.is_displayed()][0]
    preview_url = preview_element.get_attribute('src')
    label = preview_element.get_attribute('aria-label')

    filename_elements = sb.find_elements("div[aria-label^='Filename']")
    filename_element = [x for x in filename_elements if x.is_displayed()][0]
    filename = filename_element.text
    
    size_elements = sb.find_elements("span[aria-label^='Size:']")
    size_element = [x for x in size_elements if x.is_displayed()][0]
    size = size_element.text

    filesize_elements = sb.find_elements("span[aria-label^='File size:']")
    filesize_element = [x for x in filesize_elements if x.is_displayed()][0]
    filesize = filesize_element.text
 
    # sb.send_keys("html", Keys.SHIFT + "d")

    sb.download_file(preview_url)
    parsed_url = urllib.parse.urlparse(preview_url)
    filename = parsed_url.path.split('/')[-1]
    sb.assert_downloaded_file(filename)
    filepath = sb.get_path_of_downloaded_file(filename)
    with open(filepath, "rb") as imageBinary:
        img = Image.open(imageBinary)
        imgHash = str(imagehash.phash(img))
        hashInt = twos_complement(imgHash, 64) #convert from hexadecimal to 64 bit signed integer

    cursor.execute(
        "INSERT INTO hashes(hash, url, preview_url, label, filename, size, filesize) VALUES (%s, %s, %s, %s, %s, %s, %s)",
        (hashInt, url, preview_url, label, filename, size, filesize)
    )
    conn.commit()
    print(f"added image to database")
    # print(url, preview_url, label, filename, size, filesize)
    
    return context, sb

if __name__ == '__main__':
    context, sb = my_sb()
    context.__exit__(None, None, None)