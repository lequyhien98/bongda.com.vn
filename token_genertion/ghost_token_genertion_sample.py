# import jwt  # pip install pyjwt
# from datetime import datetime as date
#
# # Admin API key goes here
# key = 'AdminAPIKey'
#
# # Split the key into ID and SECRET
# _id, secret = key.split(':')
#
# # Prepare header and payload
# iat = int(date.now().timestamp())
#
# header = {'alg': 'HS256', 'typ': 'JWT', 'kid': _id}
# payload = {
#     'iat': iat,
#     'exp': iat + 5 * 60,
#     'aud': '/v3/admin/'
# }
#
# # Create the token (including decoding secret)
# ghost_token = jwt.encode(payload, bytes.fromhex(secret), algorithm='HS256', headers=header)
