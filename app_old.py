from passlib.context import CryptContext
from jwt.exceptions import InvalidTokenError, ExpiredSignatureError, InvalidSignatureError, DecodeError
import jwt
from fastapi import *
from fastapi.responses import FileResponse, JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
from pydantic import BaseModel, constr, EmailStr
from typing import Annotated, Literal
from annotated_types import MinLen
import mysql.connector
import os
import datetime
from datetime import timedelta, date, datetime, timezone
import json
import traceback
import logging

# database parameters

load_dotenv()
db_host = os.getenv("db_host")
db_user = os.getenv("db_user")
db_pw = os.getenv("db_pw")
db_database = os.getenv("db_database")
secret_key = os.getenv("jwt_secret_key")
token_valid_time = timedelta(days=7)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Pydantic classes for output

class Data(BaseModel):
    data: list[str]


class Attraction(BaseModel):
    id: int
    name: str
    category: str
    description: str
    address: str
    transport: str
    mrt: str | None
    lat: float
    lng: float
    images: list[str]


class AttractionQueryOut(BaseModel):
    nextPage: int | None
    data: list[Attraction]


class AttractionSpecifyOut(BaseModel):
    data: Attraction


class Error(BaseModel):
    error: bool
    message: str
    
# Pydantic models for "Users" API

class SigninFormData(BaseModel):
    email: EmailStr
    password: Annotated[str, MinLen(1)]

class SignupFormData(BaseModel):
    name: Annotated[str, MinLen(1)]
    email: EmailStr
    password: Annotated[str, MinLen(1)]

class UserSigninData(BaseModel):
    id: int
    name: Annotated[str, MinLen(1)]
    email: EmailStr

class UserSigninDataOut(BaseModel):
    data: UserSigninData

class TokenOut(BaseModel):
    token: str

# Classes for "Booking" API
class BookingFormData(BaseModel):
    attractionId: int
    date: date
    time: Literal["morning", "afternoon"]
    price: int

# Tags for SwaggerUI

tags_metadata = [
    {
        "name": "Attraction",
        "description": "APIs for attraction processing"
    },
    {
        "name": "MRT Station",
        "description": "API for MRT station retrieval"
    },
    {
        "name": "User",
        "description": "APIs for user CRUD and authentication"
    },
    {
        "name": "Booking",
        "description": "APIs for booking a new tour"
    },
]

## Attraction API related functions

def insert_attraction_data_nonimage(attraction):
    # non image part
    data = {}
    data["id"] = attraction[0]
    data["name"] = attraction[1]
    data["category"] = attraction[2]
    data["description"] = attraction[3]
    data["address"] = attraction[4]
    data["transport"] = attraction[5]
    data["mrt"] = attraction[6]
    data["lat"] = float(attraction[7])
    data["lng"] = float(attraction[8])
    return data


def insert_attraction_data_image(data: dict, image_result):
    # image part
    data["images"] = []
    if image_result:
        for image_url in image_result:
            data["images"].append(image_url[0])
    return data

## User API related functions

def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

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
    # hashed_pw_from_db = result[1]
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

# authenticate user, but return a boolean
def check_user_signin_status_return_data(token_data):
    try:
        decode_result = jwt.decode(token_data.token, secret_key, algorithms="HS256")
        # decode success and there is an id in the result (indicating a real user)
        if decode_result["id"]:
            return decode_result
        else:
            return False
    except Exception:
        return False

def get_token_header(authorization: str = Header(...)) -> TokenOut:
    stripped_token = authorization[len("Bearer "):]
    if not stripped_token:
        return False
    return TokenOut(token=stripped_token)

# booking APIs related functions

# get (GET) booking API
def get_user_current_cart(token_data):
    print(check_user_signin_status_return_data(token_data))
    signin_status = check_user_signin_status_return_data(token_data)
    if not check_user_signin_status_return_data(token_data):
        print("hit route 1")
        return JSONResponse(status_code=403, content={"error":True, "message": "使用者驗證失敗，請先登入"})
    # 驗證OK
    else:
        try:
            print("hit route 2")
            website_db = mysql.connector.connect(
                host=db_host, user=db_user, password=db_pw, database=db_database)
            website_db_cursor = website_db.cursor()
            var1 = signin_status["id"]
                        
            print("Fetching data")
            # Please experiment with stuff before submitting!          
            cmd = "SELECT booking_cart.attraction_id, date, time, price, attraction.id, attraction.name, attraction.address, image.url FROM booking_cart LEFT JOIN attraction ON booking_cart.attraction_id = attraction.id LEFT JOIN image ON booking_cart.attraction_id = image.attraction_id WHERE booking_cart.member_id = %s LIMIT 1"
            website_db_cursor.execute(cmd,(var1,))
            result = website_db_cursor.fetchone()
            print(result)
            if not result:
                print("No booking found...")
                return {"data": None}
            else:
                print("Found booking data!")
                response_data={}
                response_data["date"] = result[1]
                response_data["time"] = result[2]
                response_data["price"] = result[3]
                
                response_data["attraction"]={}
                response_data["attraction"]["id"] = result[4]
                response_data["attraction"]["name"] = result[5]
                response_data["attraction"]["address"] = result[6]
                response_data["attraction"]["image"] = result[7]
                
                return {"data": response_data}
        
        # Handle exceptions
        except Exception:
            traceback.print_exc()
            logging.error(f"Exception occurred: {Exception}")
            return JSONResponse(status_code=422, content={"error":True})

# add (POST) booking API
def add_trip_to_users_booking_cart(booking_details, token_data):
    print(check_user_signin_status_return_data(token_data))
    signin_status = check_user_signin_status_return_data(token_data)
    if not check_user_signin_status_return_data(token_data):
        print("hit route 1")
        return JSONResponse(status_code=403, content={"error": True, "message": "使用者驗證失敗，請先登入"})
    # 驗證OK
    else:
        try:
            print("hit route 2")
            website_db = mysql.connector.connect(
                host=db_host, user=db_user, password=db_pw, database=db_database)
            website_db_cursor = website_db.cursor()
            var1 = signin_status["id"]
            var2 = booking_details.attractionId
            var3 = booking_details.date
            var4 = booking_details.time
            var5 = booking_details.price
                        
            print("Deleting old data")   
            cmd = "DELETE FROM booking_cart WHERE member_id = %s"
            website_db_cursor.execute(cmd,(var1,))
            website_db.commit()

            print("Adding newest data")
            cmd = "INSERT INTO booking_cart (member_id, attraction_id, date, time, price) VALUES (%s, %s, %s, %s, %s)"
            website_db_cursor.execute(cmd,(var1, var2, var3, var4, var5))
            website_db.commit()

            return {"ok": True}
        
        # Handle exceptions
        except Exception:
            traceback.print_exc()
            logging.error(f"Exception occurred: {Exception}")
            return JSONResponse(status_code=422, content={"error": True, "message": "預訂失敗，請再試一次或重新整理"})

# delete (DELETE) booking API
def delete_trip_from_users_booking_cart(token_data):
    print(check_user_signin_status_return_data(token_data))
    signin_status = check_user_signin_status_return_data(token_data)
    if not check_user_signin_status_return_data(token_data):
        return JSONResponse(status_code=403, content={"error":True, "message": "使用者驗證失敗，請先登入"})
    # 驗證OK
    else:
        try:
            print("hit route 2")
            website_db = mysql.connector.connect(
                host=db_host, user=db_user, password=db_pw, database=db_database)
            website_db_cursor = website_db.cursor()
            var1 = signin_status["id"]
                        
            print("Deleting data")   
            cmd = "DELETE FROM booking_cart WHERE member_id = %s"
            website_db_cursor.execute(cmd,(var1,))
            website_db.commit()

            return {"ok": True}
        
        except Exception:
            traceback.print_exc()
            logging.error(f"Exception occurred: {Exception}")
            return JSONResponse(status_code=422, content={"error":True, "message": "刪除失敗，請再試一次或重新整理"})


# Main App

app = FastAPI()

# Static Files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Static Pages (Never Modify Code in this Block)
@app.get("/", include_in_schema=False)
async def index(request: Request):
    return FileResponse("./static/index.html", media_type="text/html")
@app.get("/attraction/{id}", include_in_schema=False)
async def attraction(request: Request, id: int):
    return FileResponse("./static/attraction.html", media_type="text/html")
@app.get("/booking", include_in_schema=False)
async def booking(request: Request):
    return FileResponse("./static/booking.html", media_type="text/html")
@app.get("/thankyou", include_in_schema=False)
async def thankyou(request: Request):
    return FileResponse("./static/thankyou.html", media_type="text/html")
# End of Static Pages

# "Attraction" API routes
# API: 取得景點資料列表，page從0開始(如果沒有下一頁，nextPage = null)


@app.get("/api/attractions", response_model=AttractionQueryOut, summary="取得景點資料列表", tags=["Attraction"],
         responses={400: {"model": Error}, 500: {"model": Error}})
async def get_attractions_by_query_string(request: Request, response: Response, page: int, keyword: str | None = None):
    # 每頁輸出筆數依據API docs先設定為12, 保留往後可調整之空間
    items_per_page = 12

    if page < 0:
        return JSONResponse(status_code=400, content=Error(error="true", message="頁碼不正確，請確認頁碼").dict())

    # initialize output
    output = {}
    output["data"] = []

    website_db = mysql.connector.connect(
        host=db_host, user=db_user, password=db_pw, database=db_database)
    website_db_cursor = website_db.cursor()

    # SELECT FROM attraction table
    # SELECT items_per_page + 1是希望知道有沒有下一頁，沒有的話可以傳回None(python)/null(js)
    if keyword:
        cmd = "SELECT id, name, category, description, address, transport, mrt, lat, lng FROM attraction WHERE mrt = %s OR name LIKE %s LIMIT %s, %s"
        website_db_cursor.execute(
            cmd, (keyword, "%" + keyword + "%", page * items_per_page, items_per_page + 1))
    else:
        cmd = "SELECT id, name, category, description, address, transport, mrt, lat, lng FROM attraction LIMIT %s, %s"
        website_db_cursor.execute(cmd, (page * items_per_page, items_per_page + 1))
    result = website_db_cursor.fetchall()
    if result:
        # 如果有下一頁，把最後一個結果丟掉，如果沒有下一頁，最後一個結果就不丟掉(保留)
        if len(result) == items_per_page + 1:
            output["nextPage"] = page + 1
            result.pop()
        else:
            output["nextPage"] = None

        for item in result:
            # non-image part
            data_without_images = insert_attraction_data_nonimage(item)

            # image part: SELECT FROM image table
            cmd = "SELECT url FROM image WHERE attraction_id = %s"
            website_db_cursor.execute(cmd, (item[0],))
            image_result = website_db_cursor.fetchall()
            data_with_images = insert_attraction_data_image(
                data_without_images, image_result)

            # append one attraction's data to output
            output["data"].append(data_with_images)
        return output

    # not found case, return empty data array
    else:
        output["nextPage"] = None
        return output

# API: 根據景點編號取得景點資料


@app.get("/api/attraction/{attractionId}", response_model=AttractionSpecifyOut, summary="根據景點編號取得景點資料", tags=["Attraction"],
         responses={400: {"model": Error}, 500: {"model": Error}})
async def get_attraction_by_id(request: Request, attractionId: int):

    # # Function to Call DB only once but at a higher memory usage
    # from test_functions import get_attraction_by_one_db_call
    # result = get_attraction_by_one_db_call(attractionId)
    # if "data" in result:
    # 	return {"data": result["data"]}
    # elif "error" in result:
    # 	return JSONResponse(status_code=400, content=Error(error=result["error"], message=result["message"]).dict())
    # else:
    # 	return JSONResponse(status_code=500, content=Error(error=result["error"], message="SOMETHING WENT WRONG").dict())

    # 目前的版本，上面有1 DB call版本
    # SELECT FROM attraction table
    website_db = mysql.connector.connect(
        host=db_host, user=db_user, password=db_pw, database=db_database)
    website_db_cursor = website_db.cursor()
    cmd = "SELECT id, name, category, description, address, transport, mrt, lat, lng FROM attraction WHERE id = %s"
    website_db_cursor.execute(cmd, (attractionId,))
    result = website_db_cursor.fetchone()
    if result:
        # non-image part: SELECT FROM image table
        data_without_images = insert_attraction_data_nonimage(result)

        # image part: SELECT FROM image table
        cmd = "SELECT url FROM image WHERE attraction_id = %s"
        website_db_cursor.execute(cmd, (result[0],))
        image_result = website_db_cursor.fetchall()
        data_with_images = insert_attraction_data_image(
            data_without_images, image_result)
        return {"data": data_with_images}

    # not found case, return error
    else:
        return JSONResponse(status_code=400, content=Error(error="true", message="景點編號不正確，請確認景點編號或聯繫管理員").dict())

# "MRT" API routes

@app.get("/api/mrts", summary="取得捷運站名稱列表", response_model=Data, tags=["MRT Station"], responses={500: {"model": Error}})
async def get_mrts(request: Request):
    # SELECT all existing MRT stations FROM attraction table
    website_db = mysql.connector.connect(
        host=db_host, user=db_user, password=db_pw, database=db_database)
    website_db_cursor = website_db.cursor()

    # 第二次嘗試: 使用SQL抓raw data 加排序輸出
    # SELECT COUNT(…) FROM … GROUP BY … ORDER BY COUNT(…)
    cmd = "SELECT mrt, COUNT(id) FROM attraction GROUP BY mrt ORDER BY count(id) DESC"
    website_db_cursor.execute(cmd)
    result = website_db_cursor.fetchall()
    output_list = [item[0] for item in result if item[0] is not None]
    # # This is equal to:
    # output_list = []
    # for item in result:
    # 	if item[0] is not None:
    # 		output_list.append(item[0])print(output_list)
    return {"data": output_list}

# "Users" API routes

# signup a new user # Note: bug fixed: everything was 422 because the request header was plaintext. => 記得要在js裡面指定header為JSON...
@app.post("/api/user", summary="註冊一個新的會員", tags=["User"])
async def signup(sign_up_credentials: SignupFormData, request: Request, response: Response):
    return create_user(email=sign_up_credentials.email, password=sign_up_credentials.password, name=sign_up_credentials.name) 

# authenticate current token in localStorage
@app.put("/api/user/auth", response_model=TokenOut, summary="登入會員帳戶", tags=["User"])
async def signin(sign_in_credentials: SigninFormData, request: Request, response: Response):
    return authenticate_user(email=sign_in_credentials.email, password=sign_in_credentials.password)

# check sign in status(predicted usage: on every page). response model integration was helped by ChatGPT
@app.get("/api/user/auth", response_model=UserSigninDataOut, summary="取得當前登入的會員資訊", tags=["User"])
async def check_signin_status(request: Request, response: Response, token_data: TokenOut = Depends(get_token_header)):
    return check_user_signin_status(token_data)


# "Booking" API routes

@app.get("/api/booking", summary="取得尚未確認下單的預定行程", tags=["Booking"])
async def get_current_cart(request: Request, response: Response, token_data: TokenOut = Depends(get_token_header)):
    return get_user_current_cart(token_data)

@app.post("/api/booking", summary="建立新的預定行程", tags=["Booking"])
async def add_trip_to_cart(booking_details: BookingFormData, request: Request, response: Response, token_data: TokenOut = Depends(get_token_header)):
    return add_trip_to_users_booking_cart(booking_details, token_data)

@app.delete("/api/booking", summary="刪除目前的預定行程", tags=["Booking"])
async def delete_trip_from_cart(request: Request, response: Response, token_data: TokenOut = Depends(get_token_header)):
    return delete_trip_from_users_booking_cart(token_data)  


# exception handlers for 422 and 500
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: Exception):	
    return JSONResponse(status_code=400, content=(Error(error="true", message="格式不正確，請確認輸入資訊").dict()))

@app.exception_handler(500)
async def internal_server_error_handler(request: Request, exc: Exception):
    return JSONResponse(status_code=500, content=(Error(error="true", message="伺服器內部異常，請聯繫管理員確認").dict()))