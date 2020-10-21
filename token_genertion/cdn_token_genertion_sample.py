import requests

url = "https://cdn1.codeprime.net/api/auth/obtain-token/"

payload = {'username': 'username',
           'password': 'password'}

response = requests.request('POST', url, data=payload)

if response.ok:
    response = response.json()
    cdn_token = response['token']
else:
    cdn_token = None
