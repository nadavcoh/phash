import os
import csv
import time
import zipfile
from seleniumbase import SB
from selenium.webdriver.common.keys import Keys
from PIL import Image
from pillow_heif import register_heif_opener
import imagehash

register_heif_opener()

def is_file_in_use(filepath):
    try:
        os.rename(filepath, filepath)
        return False
    except OSError:
        return True

def download_photos_from_urls(urls):
    download_folder = 'downloaded_photos'
    os.makedirs(download_folder, exist_ok=True)

    with SB(uc=True) as sb:
        sb.open("https://photos.google.com/login")
        # Wait for the user to complete all authentication steps
        input("Press Enter after completing authentication...")
        for url in urls:
            
            sb.open(url)
            sb.send_keys("html", "i")
            time.sleep(6)

            sb.send_keys("html", Keys.SHIFT + "d")
            time.sleep(6)
            
            download_path = sb.get_downloads_folder()
            latest_file = max([os.path.join(download_path, f) for f in os.listdir(download_path)], key=os.path.getctime)
            while latest_file.endswith('.crdownload'):
                time.sleep(1)
                latest_file = max([os.path.join(download_path, f) for f in os.listdir(download_path)], key=os.path.getctime)

            if latest_file.endswith('.zip'):
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
            while is_file_in_use(latest_file):
                time.sleep(1)
            os.rename(latest_file, os.path.join(download_folder, os.path.basename(latest_file)))

if __name__ == "__main__":
    urls = []
    with open('urls.csv', mode='r') as file:
        csv_reader = csv.reader(file)
        for row in csv_reader:
            urls.append(row[0])

    download_photos_from_urls(urls)