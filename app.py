from fastapi import *
from fastapi.responses import FileResponse, JSONResponse
from dotenv import load_dotenv
import mysql.connector, os

#database parameters
load_dotenv()
db_host=os.getenv("db_host")
db_user=os.getenv("db_user")
db_pw=os.getenv("db_pw")
db_database=os.getenv("db_database")

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

@app.get("/api/mrts")
async def index(request: Request):
	website_db = mysql.connector.connect(host=db_host,user=db_user,password=db_pw,database=db_database,ssl_disabled=True)
	website_db_cursor = website_db.cursor()
	cmd = "SELECT mrt FROM attraction"
	website_db_cursor.execute(cmd)
	result = website_db_cursor.fetchall()
	mrt_occurence_dict={}
	for item in result:
		station = item[0]
		if station == None:
			pass
		elif station not in mrt_occurence_dict:
			mrt_occurence_dict[station]=1
		else:
			mrt_occurence_dict[station]+=1
	
	#print(mrt_occurence_dict)
	mrt_occurence_dict_sorted = dict(sorted(mrt_occurence_dict.items(), key=lambda key_val: key_val[1], reverse=True))
	#print(mrt_occurence_dict_sorted)
	output_list = []
	for item in mrt_occurence_dict_sorted.items():
		output_list.append(item[0])
	#print(output_list)
	output_dict = {"data":output_list}
	
	return JSONResponse(output_dict)


@app.get("/api/attractions")
async def get_attractions_by_query_string(request: Request, page: int, keyword: str | None = None):
	if page < 1:
		return JSONResponse(status_code=400, content=({"error": True, "message": "頁碼不正確，請確認頁碼"}))
	
	output = {}
	output["nextPage"] = page + 1
	output["data"] = []
	website_db = mysql.connector.connect(host=db_host,user=db_user,password=db_pw,database=db_database)
	website_db_cursor = website_db.cursor()
	if keyword:
		cmd = "SELECT id, name, category, description, address, transport, mrt, lat, lng FROM attraction WHERE mrt = %s OR name LIKE %s LIMIT %s, 12"
		website_db_cursor.execute(cmd,(keyword, "%"+keyword+"%", (page-1)*12))
	else:
		cmd = "SELECT id, name, category, description, address, transport, mrt, lat, lng FROM attraction LIMIT %s, 12"
		website_db_cursor.execute(cmd,((page-1)*12,))
	result = website_db_cursor.fetchall()

	if result:
		for item in result:
			data = {}
			data["id"] = item[0]
			data["name"] = item[1]
			data["category"] = item[2]
			data["description"] = item[3]
			data["address"] = item[4]
			data["transport"] = item[5]
			data["mrt"] = item[6]
			data["lat"] = float(item[7])
			data["lng"] = float(item[8])

			cmd = "SELECT url FROM image WHERE attraction_id = %s"
			website_db_cursor.execute(cmd,(item[0],))
			image_result = website_db_cursor.fetchall()
			data["images"]=[]
			# print(data)
			if image_result:
				print(image_result)
				for image_url in image_result:
					data["images"].append(image_url[0])
			output["data"].append(data)
		return JSONResponse(output)
			
	else:
		return JSONResponse(output)

@app.get("/api/attraction/{attractionId}")
async def get_attraction_by_id(request: Request, attractionId: int):
	website_db = mysql.connector.connect(host=db_host,user=db_user,password=db_pw,database=db_database)
	website_db_cursor = website_db.cursor()
	cmd = "SELECT id, name, category, description, address, transport, mrt, lat, lng FROM attraction WHERE id = %s"
	website_db_cursor.execute(cmd,(attractionId,))
	result = website_db_cursor.fetchone()
	if result:
		# print(result)
		data = {}
		data["id"] = result[0]
		data["name"] = result[1]
		data["category"] = result[2]
		data["description"] = result[3]
		data["address"] = result[4]
		data["transport"] = result[5]
		data["mrt"] = result[6]
		data["lat"] = float(result[7])
		data["lng"] = float(result[8])
		cmd = "SELECT url FROM image WHERE attraction_id = %s"
	else:
		return JSONResponse(status_code=400, content=({"error": True, "message": "景點編號不正確，請確認景點編號或聯繫管理員"}))

	website_db_cursor.execute(cmd,(attractionId,))
	result = website_db_cursor.fetchall()
	if result:
		# print(result)
		data["images"]=[]
		for item in result:
			data["images"].append(item[0])
		
	##image part here
	return JSONResponse({"data": data})

#exception handler. check how to print custom responses?
#TODO: This one doesn't work!
@app.exception_handler(422)
async def internal_exception_handler(request: Request, exc: Exception):
	return JSONResponse(status_code=422, content=({"error": True, "message": "格式不正確，請確認輸入資訊"}))

@app.exception_handler(500)
async def internal_exception_handler(request: Request, exc: Exception):
	return JSONResponse(status_code=500, content=({"error": True, "message": "伺服器內部異常，請聯繫管理員確認"}))