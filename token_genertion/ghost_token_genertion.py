import jwt  # pip install pyjwt
from datetime import datetime as date

# Admin API key goes here
key_admin = '5f869d2cd70dbb1f4d667103:3fcd0fa77dd62466bf7f2059fbc62c554ee3b74980b26369cfae7e57c18f243f'
key = '6639515e8b14a6b71a3e483479'


def create_token():
    # Split the key into ID and SECRET
    _id, secret = key_admin.split(':')
    # Prepare header and payload
    iat = int(date.now().timestamp())

    header = {'alg': 'HS256', 'typ': 'JWT', 'kid': _id}
    payload = {
        'iat': iat,
        'exp': iat + 5 * 60,
        'aud': '/v3/admin/',
    }

    # Create the token (including decoding secret)
    ghost_token = jwt.encode(payload, bytes.fromhex(secret), algorithm='HS256', headers=header)
    return ghost_token
