from playwright.sync_api import sync_playwright
from pathlib import Path
from user_agents import parse
from playwright_stealth import stealth_sync

user_agent_string = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.85 Safari/537.36'

user_data_dir = Path('./session').resolve()

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            user_data_dir,
            headless=False,
            channel='chromium',
            args=[
                '--disable-features=IsolateOrigins,site-per-process',
                '--disable-blink-features=AutomationControlled',
                '--no-sandbox',
                '--disable-infobars',
                '--disable-extensions',
                '--start-maximized',
                '--window-size=1280,720'
            ],
            viewport={'width': 1280, 'height': 720},
            user_agent=user_agent_string,
            device_scale_factor=1,
        )

        page = browser.new_page()
        stealth_sync(page)  # Apply stealth settings
        page.goto('https://photos.google.com/login')

        print('Close browser once you are logged inside Google Photos')
        input("Press Enter after completing authentication...")

        # Save the authenticated session
        # context.storage_state(path=session_file)

        browser.close()

main()
