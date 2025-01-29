from seleniumbase import SB
with SB(uc=True) as sb:
    sb.open("https://photos.google.com/login")
    input("Press Enter after completing authentication...")