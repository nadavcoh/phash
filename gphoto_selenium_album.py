import os
import csv
import time
from seleniumbase import SB

def add_photos_to_album(urls, album_name):
    with SB(uc=True) as sb:
        sb.open("https://photos.google.com/login")
        # Wait for the user to complete all authentication steps
        input("Press Enter after completing authentication...")

        for url in urls:
            sb.open(url)
            sb.click('div[aria-label="More options"]')
            time.sleep(2)
            sb.click('div[aria-label="Add to album"]')
            time.sleep(2)
            sb.click(f'span:contains("{album_name}")')
            time.sleep(2)

if __name__ == "__main__":
    urls = []
    with open('urls.csv', mode='r') as file:
        csv_reader = csv.reader(file)
        for row in csv_reader:
            urls.append(row[0])

    album_name = "Family Day 2025"
    add_photos_to_album(urls, album_name)