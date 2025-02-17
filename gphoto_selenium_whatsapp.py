from seleniumbase import SB
context = SB(uc=True)
sb = context.__enter__()
sb.open("https://web.whatsapp.com")
sb.click('span[title="עדכוני ורד ואביגיל"]')