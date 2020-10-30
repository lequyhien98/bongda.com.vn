import requests

url = "https://cdn1.codeprime.net/api/auth/obtain-token/"

payload = {'username': 'bongdaxanh',
           'password': 'EBCKgkn9Lqfdt'}

response = requests.request('POST', url, data=payload)

if response.ok:
    response = response.json()
    cdn_token = response['token']
else:
    cdn_token = None
