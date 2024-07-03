import mysql.connector
import jwt
from datetime import *
from fastapi.responses import JSONResponse
from jwt.exceptions import InvalidTokenError, ExpiredSignatureError, InvalidSignatureError, DecodeError
from utils.utils import get_password_hash, verify_password
from utils.pydantic_base_models import Error

from config.db_config import db_host, db_user, db_pw, db_database, secret_key
from config.misc_config import token_valid_time

def create_user(email: str, password: str, name: str):
    website_db = mysql.connector.connect(
        host=db_host, user=db_user, password=db_pw, database=db_database)
    website_db_cursor = website_db.cursor()
    cmd = "SELECT email FROM member WHERE email = %s"
    website_db_cursor.execute(cmd, (email,))
    result = website_db_cursor.fetchone()
    if result:
        print("user already exists")
        return JSONResponse(status_code=422, content=(Error(error="true", message="此信箱已被使用").dict()))
    else:
        hashed_password = get_password_hash(password)
        print(password, hashed_password)
        cmd = "INSERT INTO member (name, email, hashed_password) VALUES (%s, %s, %s)"
        website_db_cursor.execute(cmd, (name, email, hashed_password))
        website_db.commit()
        print("added new user")
        return {"ok": True}
    
def authenticate_user(email: str, password: str):
    website_db = mysql.connector.connect(
        host=db_host, user=db_user, password=db_pw, database=db_database)
    website_db_cursor = website_db.cursor()
    cmd = "SELECT id, email, hashed_password, name FROM member WHERE email = %s"
    website_db_cursor.execute(cmd, (email,))
    result = website_db_cursor.fetchone()
    if not result:
        print("no user")
        return JSONResponse(status_code=401, content=(Error(error="true", message="帳號不存在，請確認相關資訊").dict()))
    elif not verify_password(password, hashed_password=result[2]):
        print("found user but password mismatch")
        return JSONResponse(status_code=401, content=(Error(error="true", message="密碼不正確，請確認相關資訊").dict()))
    else:
        user_information = {}
        user_information["id"] = result[0]
        user_information["email"] = result[1]
        user_information["name"] = result[3]
        time_now = datetime.now(tz=timezone.utc)
        user_information["iat"] = time_now.timestamp()
        user_information["exp"] = (time_now + token_valid_time).timestamp()
        print(user_information)
        user_token = jwt.encode(user_information, secret_key, algorithm="HS256")
        print(user_token)
        return {"token": user_token}
    
# Put in models first. maybe should be utils?
def check_user_signin_status(token_data):
    print(token_data)
    try:
        result = {}
        result["data"] = jwt.decode(token_data.token, secret_key, algorithms="HS256")
        print("Data:", result)
        # return result #Testing 20240621
        return JSONResponse(status_code=200, content=result)
    except ExpiredSignatureError:
        print("ExpiredSignatureError")
        return JSONResponse(status_code=401, content={"data": None})
    except InvalidSignatureError:
        print("InvalidSignatureError")
        return JSONResponse(status_code=401, content={"data": None})
    except DecodeError:
        print("DecodeError")
        return JSONResponse(status_code=401, content={"data": None})
    except Exception:
        print("Other exceptions")
        return JSONResponse(status_code=401, content={"data": None})
    
def check_user_signin_status_return_bool(token_data):
    try:
        decode_result = jwt.decode(token_data.token, secret_key, algorithms="HS256")
        # decode success and there is an id in the result (indicating a real user)
        if decode_result["id"]:
            return decode_result
        else:
            return False
    except Exception:
        return False
