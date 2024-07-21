import mysql.connector
from config.misc_config import items_per_page
from fastapi.responses import JSONResponse
from config.db_config import db_host, db_user, db_pw, db_database
from utils.pydantic_base_models import Error
from utils.utils import insert_attraction_data_nonimage, insert_attraction_data_image

def get_attractions_by_query_string(page: int, keyword: str | None = None):

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
    
def get_attraction_by_id(attractionId: int):
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
