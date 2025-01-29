from seleniumbase import SB
from selenium.webdriver.common.keys import Keys
import json
import time

def initialize_driver(session_file):
    try:
        with open(session_file, 'r') as f:
            session_data = json.load(f)
            cookies = session_data['cookies']
            local_storage = session_data['local_storage']
    except FileNotFoundError:
        print("Session file not found. Please authenticate first.")
        return None
    
    context = SB(uc=True)
    sb = context.__enter__()
    # Navigate to the correct domain before adding cookies
    sb.open("https://photos.google.com")
    
    for cookie in cookies:
        # Ensure the cookie domain matches the current domain
        cookie['domain'] = '.google.com'
        sb.add_cookie(cookie)
    
    sb.execute_script("window.localStorage.setItem('google_photos_local_storage', JSON.stringify(arguments[0]));", local_storage)

    # Navigate to the photos page
    sb.open("https://photos.google.com/u/0/")

    sb.send_keys("html", Keys.ARROW_RIGHT)
    sb.send_keys("html", Keys.ENTER)
    sb.send_keys("html", "i")

    url = sb.get_current_url()
    preview_elements = sb.find_elements("img[aria-label^='Photo']")
    preview_url = preview_elements[1].get_attribute('src')
    label = preview_elements[1].get_attribute('aria-label')
    filename = sb.find_elements("div[aria-label^='Filename']")[1].text
    size = sb.find_elements("span[aria-label^='Size:']")[1].text
 
    sb.send_keys("html", Keys.SHIFT + "d")
    print(url, preview_url, label, filename, size)
    return context, sb

if __name__ == '__main__':
    session_file = "session.json"
    photos_data = initialize_driver(session_file)

    if photos_data:
        for i, photo in enumerate(photos_data):
            print(f"Photo {i + 1}:")
            print(f"  URL: {photo['url']}")
            print(f"  Title: {photo['title']}")
            print(f"  Date Taken: {photo['date_taken']}")
            print(f"  Description: {photo['description']}")
            print(f"  Filename: {photo['filename']}")
            print(f"  Dimensions: {photo['dimensions']}")
            print(f"  Size: {photo['size']}")
    else:
        print('Failed to retrieve photo URLs and metadata.')