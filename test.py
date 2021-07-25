import requests
import json

r =requests.get('https://api.idkline.com/powerstates')
print(r.text)