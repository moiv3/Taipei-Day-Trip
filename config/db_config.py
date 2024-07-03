import os
from dotenv import load_dotenv
load_dotenv()

#db config

db_host = os.getenv("db_host")
db_user = os.getenv("db_user")
db_pw = os.getenv("db_pw")
db_database = os.getenv("db_database")

secret_key = os.getenv("jwt_secret_key")


#tappay config

tp_partner_key = os.getenv("tp_partner_key")
tp_merchant_id = os.getenv("tp_merchant_id")