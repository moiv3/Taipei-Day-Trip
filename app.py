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
	website_db = mysql.connector.connect(host=db_host,user=db_user,password=db_pw,database=db_database)
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


#exception handler. check how to print custom responses?
@app.exception_handler(500)
async def internal_exception_handler(request: Request, exc: Exception):
	return JSONResponse(status_code=500, content=({"error": True, "message": "Internal servor error, check log"}))