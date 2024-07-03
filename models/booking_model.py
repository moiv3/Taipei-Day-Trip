# booking APIs related functions
import mysql.connector
from config.db_config import db_host, db_user, db_pw, db_database
from fastapi.responses import JSONResponse
import traceback
import logging

from models.user_model import check_user_signin_status_return_bool

# get (GET) booking API
def get_user_current_cart(token_data):
    print(check_user_signin_status_return_bool(token_data))
    signin_status = check_user_signin_status_return_bool(token_data)
    if not check_user_signin_status_return_bool(token_data):
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
    print(check_user_signin_status_return_bool(token_data))
    signin_status = check_user_signin_status_return_bool(token_data)
    if not check_user_signin_status_return_bool(token_data):
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
    print(check_user_signin_status_return_bool(token_data))
    signin_status = check_user_signin_status_return_bool(token_data)
    if not check_user_signin_status_return_bool(token_data):
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
