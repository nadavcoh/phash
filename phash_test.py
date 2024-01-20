# python3.12 -m venv venv
# source venv/bin/activate
# pip install imagehash pillow pillow-heif google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
from PIL import Image
import imagehash
from pillow_heif import register_heif_opener

register_heif_opener()

photo_url1 = "img/pic3.jpg"
photo_url2 = "img/IMG_0246.jpg"

img1 = Image.open(photo_url1)
# print(img1.info)
photo_hash1 = (imagehash.phash(img1))

img2 = Image.open(photo_url2)
photo_hash2 = (imagehash.phash(img2))

print (photo_hash1)
print (photo_hash2)
print (photo_hash1 == photo_hash2)
print (photo_hash1 - photo_hash2)