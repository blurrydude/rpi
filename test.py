import requests
import json

r =requests.get('https://api.idkline.com/states')
print(r.text)