from seleniumbase import SB
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
    
    with SB(uc=True) as sb:
        # Navigate to the correct domain before adding cookies
        sb.open("https://photos.google.com")
        
        for cookie in cookies:
            # Ensure the cookie domain matches the current domain
            cookie['domain'] = '.google.com'
            sb.driver.add_cookie(cookie)
        
        sb.execute_script("window.localStorage.setItem('google_photos_local_storage', JSON.stringify(arguments[0]));", local_storage)

        # Navigate to the photos page
        sb.open("https://photos.google.com/u/0/")

        # Wait for photos to load
        sb.wait_for_selector("div[data-photo-index]")

        # Get the URLs and metadata of the first two photos
        photos_data = []
        for index in range(2):
            photo = sb.query_selector(f"div[data-photo-index='{index}']")
            if photo:
                photo.click()
                time.sleep(2)  # Ensure the photo is fully loaded
                photo_element = sb.query_selector("img[aria-label='Photo']")
                photo_url = photo_element.get_attribute('src')
                metadata = {}

                # Extract metadata
                metadata['url'] = photo_url
                metadata['title'] = sb.query_selector("span[aria-label='Title']").inner_text() if sb.query_selector("span[aria-label='Title']") else 'N/A'
                metadata['date_taken'] = sb.query_selector("span[aria-label='Date']").inner_text() if sb.query_selector("span[aria-label='Date']") else 'N/A'
                metadata['description'] = sb.query_selector("span[aria-label='Description']").inner_text() if sb.query_selector("span[aria-label='Description']") else 'N/A'
                
                # Extract additional metadata: filename, dimensions, and size
                metadata['filename'] = photo_element.get_attribute('alt') if photo_element.get_attribute('alt') else 'N/A'
                metadata['dimensions'] = f"{photo_element.get_attribute('naturalWidth')} x {photo_element.get_attribute('naturalHeight')}" if photo_element else 'N/A'
                metadata['size'] = sb.query_selector("span[aria-label='File size']").inner_text() if sb.query_selector("span[aria-label='File size']") else 'N/A'

                photos_data.append(metadata)

                # Click the right arrow to navigate to the next photo
                next_button = sb.query_selector("button[aria-label='Next']")
                if next_button:
                    next_button.click()
                    time.sleep(2)  # Ensure the next photo is fully loaded
                else:
                    break
            else:
                break

        return photos_data

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