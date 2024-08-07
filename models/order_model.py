from datetime import *
from utils.pydantic_base_models import *
from config.db_config import db_host, db_user, db_pw, db_database, tp_partner_key, tp_merchant_id
from fastapi.responses import JSONResponse
import mysql.connector
import json
import traceback
import requests

from models.user_model import check_user_signin_status_return_bool


def add_unpaid_entry_to_order_table(user_sign_in_status, OrderFormData: OrderFormData):
    # add entry to tour_order table, mark as unpaid
    try:
        website_db = mysql.connector.connect(
        host=db_host, user=db_user, password=db_pw, database=db_database)
        website_db_cursor = website_db.cursor()

        # format of booking_number = TDT202407020001 (TDT/20240702/0001), 0001 means the n-th order today.

        # to get the n-th order today, use query below to get existing orders today, then add 1
        current_date = datetime.now().date()
        cmd = "SELECT COUNT(*) FROM tour_order WHERE DATE(order_datetime) = %s"
        website_db_cursor.execute(cmd, (current_date,))
        today_booking_count = website_db_cursor.fetchone()[0]

        booking_number = "TDT" + str(current_date.strftime('%Y%m%d')) + str(today_booking_count + 1).zfill(4)
        print(booking_number)
        
        cmd = "INSERT INTO tour_order (id, member_id, attraction_id, date, time, price, contact_name, contact_email, contact_phone) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
        

        # print(booking_number,
        #         user_sign_in_status["id"],
        #         OrderFormData.order.trip.attraction.id,
        #         OrderFormData.order.trip.date,
        #         OrderFormData.order.trip.time,
        #         OrderFormData.order.price,
        #         OrderFormData.order.contact.name,
        #         OrderFormData.order.contact.email,
        #         OrderFormData.order.contact.phone)
        
        website_db_cursor.execute(cmd, (booking_number,
                                        user_sign_in_status["id"],
                                        OrderFormData.order.trip.attraction.id,
                                        OrderFormData.order.trip.date,
                                        OrderFormData.order.trip.time,
                                        OrderFormData.order.price,
                                        OrderFormData.order.contact.name,
                                        OrderFormData.order.contact.email,
                                        OrderFormData.order.contact.phone))
        website_db.commit()

        return booking_number
    
    except Exception:
        traceback.print_exc()
        return False


def tappay_pay_by_prime(OrderFormData: OrderFormData):
    tappay_headers = {"Content-Type": "application/json", "x-api-key": tp_partner_key}
    tappay_request_body = {
        # prime is here
        "prime": OrderFormData.prime,
        # environment variables for these
        "partner_key": tp_partner_key,
        "merchant_id": tp_merchant_id,
        "amount": OrderFormData.order.price,
        # strip attraction name for string(100) limit
        "details": "TaipeiDayTripService" + OrderFormData.order.trip.attraction.name[:10],
        # we will assume same cardholder info as contact info
        "cardholder": {"phone_number": OrderFormData.order.contact.phone, "name": OrderFormData.order.contact.name, "email": OrderFormData.order.contact.email}
    }
    print(tappay_request_body)
    res = requests.post('https://sandbox.tappaysdk.com/tpc/payment/pay-by-prime', headers=tappay_headers, json=tappay_request_body)
    response = json.loads(res.text)
    print(response)
    return response


def process_tappay_response(tappay_response, booking_number, user_sign_in_status, OrderFormData: OrderFormData):

    website_db = mysql.connector.connect(
    host=db_host, user=db_user, password=db_pw, database=db_database)
    website_db_cursor = website_db.cursor()

    order_response = {}
    order_response["data"] = {}
    order_response["data"]["number"] = booking_number
    order_response["data"]["payment"] = {}
    order_response["data"]["payment"]["status"] = tappay_response["status"]
    order_response["data"]["payment"]["message"] = tappay_response["msg"]

    if tappay_response["status"] == 0:
        print("Payment success!")
        # change to paid in table "tour_order"
        # website_db_cursor = website_db.cursor()
        cmd = "UPDATE tour_order SET paid = 1 WHERE id = %s"
        website_db_cursor.execute(cmd,(booking_number,))
        website_db.commit()

        # record payment to table "payment"
        cmd = "INSERT INTO payment (order_id, success, amount, response) VALUES (%s, %s, %s, %s)"
        website_db_cursor.execute(cmd,(booking_number,
                                       1,
                                       OrderFormData.order.price,
                                       json.dumps(tappay_response)))
        website_db.commit()

        # since order & payment success, delete booking cart
        print("Order & payment success, deleting user's booking cart")   
        cmd = "DELETE FROM booking_cart WHERE member_id = %s"
        website_db_cursor.execute(cmd,(user_sign_in_status["id"],))
        website_db.commit()

        # return success to front end
        print(order_response)
        return order_response

    else:
        print("Payment unsuccessful. See above response for details.")
        # no change in db paid status

        # record payment to table "payment"
        cmd = "INSERT INTO payment (order_id, success, amount, response) VALUES (%s, %s, %s, %s)"
        website_db_cursor.execute(cmd,(booking_number,
                                       0,
                                       OrderFormData.order.price,
                                       json.dumps(tappay_response)))
        website_db.commit()

        # return failure to front end
        print(order_response)
        return order_response


def get_order_by_order_number(orderNumber, token_data):

    signin_status = check_user_signin_status_return_bool(token_data)
    if not signin_status:
        print("Auth unsuccessful, responding with 403")
        return JSONResponse(status_code=403, content={"error": True, "message": "使用者驗證失敗"})

    website_db = mysql.connector.connect(
    host=db_host, user=db_user, password=db_pw, database=db_database)
    website_db_cursor = website_db.cursor()
    cmd = "SELECT tour_order.id, tour_order.price, tour_order.date, tour_order.time, attraction.id, attraction.name, attraction.address, image.url, tour_order.contact_name, tour_order.contact_email, tour_order.contact_phone, tour_order.paid, tour_order.member_id FROM tour_order LEFT JOIN attraction ON tour_order.attraction_id = attraction.id LEFT JOIN image ON tour_order.attraction_id = image.attraction_id WHERE tour_order.id = %s LIMIT 1"
    website_db_cursor.execute(cmd,(orderNumber,))
    result = website_db_cursor.fetchone()
    if not result:
        print("No data found")
        return {"data": None}
    # result[12] = tour_order.member_id
    elif signin_status["id"] != result[12]:
        print("Found data but different signed-in user")
        return JSONResponse(status_code=403, content={"error": True, "message": "使用者驗證失敗"})
    else:
        print("Found data, building response")
        response_dict = {}
        response_dict["data"] = {}
        
        response_dict["data"]["number"] = result[0]
        response_dict["data"]["price"] = result[1]
        
        response_dict["data"]["trip"] = {}
        response_dict["data"]["trip"]["date"] = result[2]
        response_dict["data"]["trip"]["time"] = result[3]

        response_dict["data"]["trip"]["attraction"] = {}
        response_dict["data"]["trip"]["attraction"]["id"] = result[4]
        response_dict["data"]["trip"]["attraction"]["name"] = result[5]
        response_dict["data"]["trip"]["attraction"]["address"] = result[6]
        response_dict["data"]["trip"]["attraction"]["image"] = result[7]

        response_dict["data"]["contact"] = {}
        response_dict["data"]["contact"]["name"] = result[8]
        response_dict["data"]["contact"]["email"] = result[9]
        response_dict["data"]["contact"]["phone"] = result[10]

        response_dict["data"]["status"] = result[11]

        return response_dict
    
    
def place_order_and_process_payment(OrderFormData, token_data):
    # we can get member id from token, other info from FormData
    signin_status = check_user_signin_status_return_bool(token_data)

    if not signin_status:
        print("Auth unsuccessful, responding with 403")
        return JSONResponse(status_code=403, content={"error": True, "message": "使用者驗證失敗"})
    
    else:
        booking_number = add_unpaid_entry_to_order_table(signin_status, OrderFormData) # model
        if not booking_number:
            return JSONResponse(status_code=500, content={"error": True, "message": "無法新增資料，請聯繫管理員確認"})
        
        tappay_response = tappay_pay_by_prime(OrderFormData) # controller? model? 
        # if error, still returns json, just process it

        return process_tappay_response(tappay_response, booking_number, signin_status, OrderFormData) # model
