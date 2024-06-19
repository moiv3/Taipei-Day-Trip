from passlib.context import CryptContext
from jwt.exceptions import InvalidTokenError, ExpiredSignatureError, InvalidSignatureError, DecodeError
import jwt
from fastapi import *
from fastapi.responses import FileResponse, JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
from pydantic import BaseModel
import mysql.connector
import os
import datetime
from datetime import *

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


# database parameters
load_dotenv()
db_host = os.getenv("db_host")
db_user = os.getenv("db_user")
db_pw = os.getenv("db_pw")
db_database = os.getenv("db_database")
secret_key = os.getenv("jwt_secret_key")
token_valid_time = timedelta(days=7)


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
]

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

# API: 取得捷運站名稱列表


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

    """
    # 第一次嘗試: 使用SQL抓raw data, 使用python排序輸出
    cmd = "SELECT mrt FROM attraction"
    website_db_cursor.execute(cmd)
    result = website_db_cursor.fetchall()

    #將SQL抓回來的捷運站做次數統計並排序輸出
    mrt_occurence_dict = {}
    for item in result:
        station = item[0]
        if station == None:
            pass
        elif station not in mrt_occurence_dict:
            mrt_occurence_dict[station] = 1
        else:
            mrt_occurence_dict[station] += 1

    mrt_occurence_dict_sorted = dict(sorted(
        mrt_occurence_dict.items(), key=lambda key_val: key_val[1], reverse=True))
    output_list = []
    for item in mrt_occurence_dict_sorted.items():
        output_list.append(item[0])
    return {"data": output_list}
    """

"""Test functions 20240614"""
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
fake_db = {
    "y": {
        "username": "y",
        # "password": "r",
        "hashed_password": "$2b$12$WTbKhGwgvcnwFYZMM0LN7ONCHWjjeV7FViUTGW/SqhoRbV7O/RYry"
        # hashed_password is verified
    }
}


class User(BaseModel):
    username: str


class UserInDB(User):
    hashed_password: str


def get_password_hash(password):
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)

def create_user(db, username: str, password: str, name: str):
    website_db = mysql.connector.connect(
        host=db_host, user=db_user, password=db_pw, database=db_database)
    website_db_cursor = website_db.cursor()
    cmd = "SELECT username FROM member WHERE username = %s"
    website_db_cursor.execute(cmd, (username,))
    result = website_db_cursor.fetchone()
    if result:
        print("user already exists")
        return {"error": True, "message": "使用者名稱已被使用"}
    else:
        hashed_password = get_password_hash(password)
        print(password, hashed_password)
        cmd = "INSERT INTO member (username, hashed_password, name, email) VALUES (%s, %s, %s, %s)"
        website_db_cursor.execute(cmd, (username, hashed_password, name, "example@example.com"))
        website_db.commit()
        print("added new user")
        return {"ok": True}


def authenticate_user(fake_db, username: str, password: str):
    website_db = mysql.connector.connect(
        host=db_host, user=db_user, password=db_pw, database=db_database)
    website_db_cursor = website_db.cursor()
    cmd = "SELECT username, hashed_password, name, email FROM member WHERE username = %s"
    website_db_cursor.execute(cmd, (username,))
    result = website_db_cursor.fetchone()
    # hashed_pw_from_db = result[1]
    if not result:
        print("no user")
        return JSONResponse(status_code=401, content=(Error(error="true", message="帳號不存在，請確認相關資訊").dict()))
    elif not verify_password(password, hashed_password=result[1]):
        print("found user but password mismatch")
        return JSONResponse(status_code=401, content=(Error(error="true", message="帳號或密碼錯誤，請確認相關資訊").dict()))
    else:
        user_information = {}
        user_information["username"] = result[0]
        user_information["name"] = result[2]
        user_information["email"] = result[3]
        time_now = datetime.now(tz=timezone.utc)
        user_information["iat"] = time_now.timestamp()
        user_information["exp"] = (time_now + token_valid_time).timestamp()
        print(user_information)
        user_token = jwt.encode(user_information, secret_key, algorithm="HS256")
        print(user_token)
        return {"token": user_token}
    # 做到可以比較密碼和DB中hashed的密碼了!
    # return some kind of token back!
    
    
    """
    print(fake_db)
    print(username)
    user = get_user(fake_db, username)
    print(user)
    if not user:
        print("no user")
        return False
    if not verify_password(password, user.hashed_password):
        print("verify failed")
        return False
    return user
    """
# Not implemented yet -> implement before PR!
class SigninFormData(BaseModel):
    username: str
    password: str


def check_token_validity(token_json):
    print(token_json)
    return

@app.post("/api/user")
async def signup(request: Request, response: Response):
# async def signin(request: Request, response: Response, username_name: str | None = Form(None), password_name: str | None = Form(None)):
    print(await request.json())
    sign_up_credentials = await request.json()
    return create_user(db=db_database, username=sign_up_credentials["username"], password=sign_up_credentials["password"], name=sign_up_credentials["name"])

@app.put("/api/user/auth")
async def signin(request: Request, response: Response):
# async def signin(request: Request, response: Response, username_name: str | None = Form(None), password_name: str | None = Form(None)):
    print(await request.json())
    sign_in_credentials = await request.json()
    return authenticate_user(fake_db, username=sign_in_credentials["username"], password=sign_in_credentials["password"])

@app.get("/api/user/auth")
async def checkSignInStatus(request: Request, response: Response): # token?
    print(request.headers)
    token_json = request.headers["authorization"].split("Bearer ")[1]
    print(token_json)
    try:
        result = {}
        result["data"] = jwt.decode(token_json, secret_key, algorithms="HS256")
        print("Hit route 1")
        return result
        # TODO: data should use pydantic classes for auto sanitize
    except ExpiredSignatureError:
        print("Hit route 2")
        print(Exception)
        return {"data": None, "message": "Token expired, please login again! (ExpiredSignatureError)"}
    except InvalidSignatureError:
        return {"data": None, "message": "Token invalid, please login again! (InvalidSignatureError)"}
    except DecodeError:
        return {"data": None, "message": "Token invalid, please login again! (DecodeError)"}

#exception handlers for 422 and 500
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: Exception):	
    return JSONResponse(status_code=400, content=(Error(error="true", message="格式不正確，請確認輸入資訊").dict()))

@app.exception_handler(500)
async def internal_server_error_handler(request: Request, exc: Exception):
    return JSONResponse(status_code=500, content=(Error(error="true", message="伺服器內部異常，請聯繫管理員確認").dict()))