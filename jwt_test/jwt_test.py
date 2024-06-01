import jwt

payload_data = {
    "team": "Leisure Land",
    "player": "DON",
    "Lv12_max_scores": 4
}

my_secret = "fffff"

token = jwt.encode(
    payload=payload_data,
    key=my_secret
)

print(token)

decoded_key = jwt.decode(token, key='ffffff', algorithms=['HS256', ])

print(decoded_key)