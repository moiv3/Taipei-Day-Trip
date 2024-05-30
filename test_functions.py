from fastapi.responses import FileResponse, JSONResponse
import mysql.connector, os
from dotenv import load_dotenv
from pydantic import BaseModel

class Error(BaseModel):
	error: bool
	message: str
     
def get_attraction_by_one_db_call(attractionId):

    load_dotenv()
    db_host = os.getenv("db_host")
    db_user = os.getenv("db_user")
    db_pw = os.getenv("db_pw")
    db_database = os.getenv("db_database")

    website_db = mysql.connector.connect(host=db_host,user=db_user,password=db_pw,database=db_database)
    website_db_cursor = website_db.cursor()
    cmd = "SELECT attraction.id, attraction.name, attraction.category, attraction.description, attraction.address, attraction.transport, attraction.mrt, attraction.lat, attraction.lng, image.url FROM attraction LEFT JOIN image on attraction.id = image.attraction_id WHERE attraction.id = %s"
    website_db_cursor.execute(cmd,(attractionId,))
    result = website_db_cursor.fetchall()
    
    if result:
        data = {}
        first_line_flag = True
        for attraction in result:	
            if first_line_flag == True:
                data["id"] = attraction[0]
                data["name"] = attraction[1]
                data["category"] = attraction[2]
                data["description"] = attraction[3]
                data["address"] = attraction[4]
                data["transport"] = attraction[5]
                data["mrt"] = attraction[6]
                data["lat"] = float(attraction[7])
                data["lng"] = float(attraction[8])
                data["images"] = []
                first_line_flag = False			
            if attraction[9]:
                data["images"].append(attraction[9])

        print(data)
        return {"data": data}
    
    #not found case, return error
    else:
        return {"error": True, "message": "景點編號不正確，請確認景點編號或聯繫管理員"} #JSONResponse(status_code=400, content=Error(error="true", message="景點編號不正確，請確認景點編號或聯繫管理員").dict())