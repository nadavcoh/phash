from playwright.sync_api import sync_playwright
from playwright_stealth import stealth_sync

with sync_playwright() as p:
    for browser_type in [p.chromium, p.firefox, p.webkit]:
        browser = browser_type.launch(headless=False)
        page = browser.new_page()
        stealth_sync(page)
        page.goto('https://photos.google.com/login')
        input("Press Enter after completing authentication...")
        browser.close()