from playwright.sync_api import sync_playwright

def manual_authentication(session_file):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            viewport={"width": 1280, "height": 800},
            java_script_enabled=True,
            accept_downloads=True,
            bypass_csp=True,
            ignore_https_errors=True
        )
        page = context.new_page()

        # Navigate to Google Photos login page
        page.goto("https://photos.google.com/login")

        # Wait for the user to complete all authentication steps
        print("Please log in to your Google account and complete any authentication steps in the browser.")
        input("Press Enter after completing authentication...")

        # Save the authenticated session
        context.storage_state(path=session_file)

        browser.close()

if __name__ == '__main__':
    session_file = "session.json"
    manual_authentication(session_file)
