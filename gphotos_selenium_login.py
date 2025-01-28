from seleniumbase import SB
import json

def manual_authentication(session_file):
    with SB(uc=True) as sb:
        # Navigate to Google Photos login page
        sb.open("https://photos.google.com/login")
        # Wait for the user to complete all authentication steps
        input("Press Enter after completing authentication...")
        
        # Save cookies and local storage
        cookies = sb.driver.get_cookies()
        local_storage = sb.execute_script("return window.localStorage;")
        
        with open(session_file, 'w') as f:
            json.dump({'cookies': cookies, 'local_storage': local_storage}, f)

if __name__ == '__main__':
    session_file = "session.json"
    manual_authentication(session_file)