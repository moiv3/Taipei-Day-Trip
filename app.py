from fastapi import *
from fastapi.responses import FileResponse, JSONResponse
from fastapi.exceptions import RequestValidationError
from dotenv import load_dotenv
from pydantic import BaseModel
import mysql.connector, os

def insert_attraction_data_nonimage(attraction):
	#non image part
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
	#image part
	data["images"] = []
	if image_result:
		for image_url in image_result:
			data["images"].append(image_url[0])	
	return data

#database parameters
load_dotenv()
db_host = os.getenv("db_host")
db_user = os.getenv("db_user")
db_pw = os.getenv("db_pw")
db_database = os.getenv("db_database")

#Pydantic classes for output
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
	nextPage: int
	data: list[Attraction]

class AttractionSpecifyOut(BaseModel):
	data: Attraction

class Error(BaseModel):
	error: bool
	message: str

#Tags for SwaggerUI
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

app=FastAPI()

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

#API: 取得景點資料列表
@app.get("/api/attractions", response_model = AttractionQueryOut, summary = "取得景點資料列表", tags = ["Attraction"],
		 responses = {400:{"model":Error}, 500:{"model":Error}})
async def get_attractions_by_query_string(request: Request, response: Response, page: int, keyword: str | None = None):
	#每頁輸出個數先設定為12, 保留往後可調整之空間
	items_per_page = 12
	
	if page < 1:
		return JSONResponse(status_code=400, content=Error(error="true", message="頁碼不正確，請確認頁碼").model_dump())
	
	#initialize output
	output = {}
	output["nextPage"] = page + 1
	output["data"] = []

	website_db = mysql.connector.connect(host=db_host,user=db_user,password=db_pw,database=db_database)
	website_db_cursor = website_db.cursor()

	#SELECT FROM attraction table
	if keyword:
		cmd = "SELECT id, name, category, description, address, transport, mrt, lat, lng FROM attraction WHERE mrt = %s OR name LIKE %s LIMIT %s, %s"
		website_db_cursor.execute(cmd,(keyword, "%"+keyword+"%", (page-1)*items_per_page, items_per_page))
	else:
		cmd = "SELECT id, name, category, description, address, transport, mrt, lat, lng FROM attraction LIMIT %s, %s"
		website_db_cursor.execute(cmd,((page-1)*items_per_page, items_per_page))
	result = website_db_cursor.fetchall()
	if result:
		for item in result:
			#non-image part
			data_without_images = insert_attraction_data_nonimage(item)

			#image part: SELECT FROM image table
			cmd = "SELECT url FROM image WHERE attraction_id = %s"
			website_db_cursor.execute(cmd,(item[0],))
			image_result = website_db_cursor.fetchall()
			data_with_images = insert_attraction_data_image(data_without_images, image_result)

			#append one attraction's data to output
			output["data"].append(data_with_images)
		return output

	#not found case, return empty data array	
	else:
		return output

#API: 根據景點編號取得景點資料
@app.get("/api/attraction/{attractionId}", response_model = AttractionSpecifyOut, summary = "根據景點編號取得景點資料", tags = ["Attraction"],
		 responses={400:{"model":Error}, 500:{"model":Error}})
async def get_attraction_by_id(request: Request, attractionId: int):
	#SELECT FROM attraction table
	website_db = mysql.connector.connect(host=db_host,user=db_user,password=db_pw,database=db_database)
	website_db_cursor = website_db.cursor()
	cmd = "SELECT id, name, category, description, address, transport, mrt, lat, lng FROM attraction WHERE id = %s"
	website_db_cursor.execute(cmd,(attractionId,))
	result = website_db_cursor.fetchone()
	if result:
		#non-image part: SELECT FROM image table
		data_without_images = insert_attraction_data_nonimage(result)
		
		#image part: SELECT FROM image table
		cmd = "SELECT url FROM image WHERE attraction_id = %s"
		website_db_cursor.execute(cmd,(result[0],))
		image_result = website_db_cursor.fetchall()
		data_with_images = insert_attraction_data_image(data_without_images, image_result)
		return {"data": data_with_images}
	
	#not found case, return error
	else:
		return JSONResponse(status_code=400, content=Error(error="true", message="景點編號不正確，請確認景點編號或聯繫管理員").model_dump())

#API: 取得捷運站名稱列表
@app.get("/api/mrts", summary = "取得捷運站名稱列表", response_model = Data, tags = ["MRT Station"], responses = {500:{"model":Error}})
async def get_mrts(request: Request):
	#SELECT all existing MRT stations FROM attraction table
	website_db = mysql.connector.connect(host=db_host,user=db_user,password=db_pw,database=db_database)
	website_db_cursor = website_db.cursor()
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
	
	mrt_occurence_dict_sorted = dict(sorted(mrt_occurence_dict.items(), key=lambda key_val: key_val[1], reverse=True))
	output_list = []
	for item in mrt_occurence_dict_sorted.items():
		output_list.append(item[0])
	return {"data": output_list}

#exception handlers for 422 and 500
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: Exception):	
	return JSONResponse(status_code=400, content=(Error(error="true", message="格式不正確，請確認輸入資訊").model_dump()))

@app.exception_handler(500)
async def internal_server_error_handler(request: Request, exc: Exception):
	return JSONResponse(status_code=500, content=(Error(error="true", message="伺服器內部異常，請聯繫管理員確認").model_dump()))