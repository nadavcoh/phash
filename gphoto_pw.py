from playwright.sync_api import sync_playwright
import time

def initialize_driver(session_file):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(storage_state=session_file)
        page = context.new_page()
        return page

def get_photo_links_and_metadata(page):
    # Navigate to the photos page
    page.goto("https://photos.google.com/u/0/")

    # Wait for photos to load
    page.wait_for_selector("div[data-photo-index]")

    # Get the URLs and metadata of the first two photos
    photos_data = []
    for index in range(2):
        photo = page.query_selector(f"div[data-photo-index='{index}']")
        if photo:
            photo.click()
            time.sleep(2)  # Ensure the photo is fully loaded
            photo_element = page.query_selector("img[aria-label='Photo']")
            photo_url = photo_element.get_attribute('src')
            metadata = {}

            # Extract metadata
            metadata['url'] = photo_url
            metadata['title'] = page.query_selector("span[aria-label='Title']").inner_text() if page.query_selector("span[aria-label='Title']") else 'N/A'
            metadata['date_taken'] = page.query_selector("span[aria-label='Date']").inner_text() if page.query_selector("span[aria-label='Date']") else 'N/A'
            metadata['description'] = page.query_selector("span[aria-label='Description']").inner_text() if page.query_selector("span[aria-label='Description']") else 'N/A'
            
            # Extract additional metadata: filename, dimensions, and size
            metadata['filename'] = photo_element.get_attribute('alt') if photo_element.get_attribute('alt') else 'N/A'
            metadata['dimensions'] = f"{photo_element.get_attribute('naturalWidth')} x {photo_element.get_attribute('naturalHeight')}" if photo_element else 'N/A'
            metadata['size'] = page.query_selector("span[aria-label='File size']").inner_text() if page.query_selector("span[aria-label='File size']") else 'N/A'

            photos_data.append(metadata)

            # Click the right arrow to navigate to the next photo
            next_button = page.query_selector("button[aria-label='Next']")
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
    page = initialize_driver(session_file)
    try:
        photos_data = get_photo_links_and_metadata(page)
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
    finally:
        page.context.close()