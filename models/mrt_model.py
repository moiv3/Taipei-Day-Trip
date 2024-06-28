import mysql.connector
from config.db_config import db_host, db_user, db_pw, db_database

def get_mrts():
    # SELECT all existing MRT stations FROM attraction table
    website_db = mysql.connector.connect(
        host=db_host, user=db_user, password=db_pw, database=db_database)
    website_db_cursor = website_db.cursor()

    cmd = "SELECT mrt, COUNT(id) FROM attraction GROUP BY mrt ORDER BY count(id) DESC"
    website_db_cursor.execute(cmd)
    result = website_db_cursor.fetchall()
    output_list = [item[0] for item in result if item[0] is not None]

    return {"data": output_list}