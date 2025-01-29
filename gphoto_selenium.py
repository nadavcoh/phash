from seleniumbase import SB
from selenium.webdriver.common.keys import Keys
from time import sleep

def my_sb():
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

    print(url, preview_url, label, filename, size, filesize)
    
    return context, sb

if __name__ == '__main__':
    context, sb = my_sb()
    context.__exit__(None, None, None)