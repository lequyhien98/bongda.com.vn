import requests  # pip install requests
import jwt  # pip install pyjwt
from datetime import datetime as date

# Admin API key goes here
key = '5f855492d70dbb1f4d6670a9:973462cc2b98778481070f47ece548f879d8f23a017a33faddb4b2fff3e81cfa'

# Split the key into ID and SECRET
_id, secret = key.split(':')

# Prepare header and payload
iat = int(date.now().timestamp())

header = {'alg': 'HS256', 'typ': 'JWT', 'kid': _id}
payload = {
    'iat': iat,
    'exp': iat + 5 * 60,
    'aud': '/v3/admin/'
}

# Create the token (including decoding secret)
token = jwt.encode(payload, bytes.fromhex(secret), algorithm='HS256', headers=header)


