import json
import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

file_path = os.getenv("initial_json_file_path_local")

# database parameters [Week7: changed to environment variables]
db_host = os.getenv("db_host")
db_user = os.getenv("db_user")
db_pw = os.getenv("db_pw")
db_database = os.getenv("db_database")

# function to split a long string with http as the delimiter


def split_string_and_add_delimiter_only_pics(input_string, delimiter):
    """output = []
    for item in [delimiter+fragment for fragment in input_string.split(delimiter) if fragment]:
        print(item[-3:].lower())
        if item[-3:].lower() == "jpg" or item[-3:].lower() == "png":
            output.append(item)
    return output

    return [delimiter+fragment for fragment in input_string.split(delimiter) if fragment]
    """
    return [delimiter+fragment for fragment in input_string.split(delimiter) if (fragment[-3:].lower() == "jpg" or fragment[-3:].lower() == "png")]

# print (split_string_and_add_delimiter("https://www.travel.taipei/d_upload_ttn/sceneadmin/image/A0/B0/C0/D0/E197/F323/522aa425-345c-4ac4-96b8-b21a33f165ca.JPGhttps://www.travel.taipei/d_upload_ttn/sceneadmin/image/A0/B0/C0/D0/E197/F321/c0db5455-2538-44ac-922a-518e4215f072.JPGhttps://www.travel.taipei/d_upload_ttn/sceneadmin/image/A0/B0/C0/D0/E197/F324/ecf61f88-92ed-49ad-8a40-4bdc00dff585.JPGhttps://www.travel.taipei/d_upload_ttn/sceneadmin/image/A0/B0/C0/D0/E197/F325/59bd3a58-0d88-43a7-9a9e-72fd88734275.JPGhttps://www.travel.taipei/d_upload_ttn/sceneadmin/image/A0/B0/C0/D0/E197/F326/5e2be319-957c-4eff-bf29-a2a71c931260.JPGhttps://www.travel.taipei/d_upload_ttn/sceneadmin/image/A0/B0/C0/D9/E766/F606/8e98d96f-0666-4e4d-a824-3049a82025e1.JPGhttps://www.travel.taipei/d_upload_ttn/sceneadmin/image/A0/B0/C0/D6/E266/F417/01f9c74a-b87a-4a91-9070-3d9310de8843.JPGhttps://www.travel.taipei/d_upload_ttn/sceneadmin/image/A0/B0/C0/D9/E366/F347/b49bae58-e9b5-42b4-a210-11da279654ce.JPG","http"))

def load_json_to_database():
  # read file
  with open(file_path, "r", encoding="utf-8") as file:
      file_inputted = file.read()
      file_jsonloaded = json.loads(file_inputted)

      # connect to database
      website_db = mysql.connector.connect(
          host=db_host, user=db_user, password=db_pw, database=db_database)
      website_db_cursor = website_db.cursor()

      for item in file_jsonloaded["result"]["results"]:
          # add attraction data
          name = item["name"]
          category = item["CAT"]
          description = item["description"]
          address = item["address"]
          transport = item["direction"]
          mrt = item["MRT"]
          lat = item["latitude"]
          lng = item["longitude"]
          # print(name, category, description, address, transport, mrt, lat, lng)
          print(name, category)
          cmd = "INSERT IGNORE INTO attraction (name, category, description, address, transport, mrt, lat, lng) VALUES (%s, %s, %s, %s, %s, %s, %s, %s);"
          website_db_cursor.execute(
              cmd, (name, category, description, address, transport, mrt, lat, lng))
          website_db.commit()

          # add image data
          name = item["name"]
          cmd = "SELECT id FROM attraction WHERE name = %s;"
          website_db_cursor.execute(cmd, (name,))
          result = website_db_cursor.fetchone()
          attraction_id = result[0]
          img_list = split_string_and_add_delimiter_only_pics(
              item["file"], "http")
          for img_no in range(len(img_list)):
              print(attraction_id, img_no, img_list[img_no])
              cmd = "INSERT IGNORE INTO image (attraction_id, image_no_of_attraction, url) VALUES (%s, %s, %s);"
              website_db_cursor.execute(
                  cmd, (attraction_id, img_no, img_list[img_no]))
              website_db.commit()

"""
DB Schema:

mysql> desc attraction;
+-------------+---------------+------+-----+---------+----------------+
| Field       | Type          | Null | Key | Default | Extra          |
+-------------+---------------+------+-----+---------+----------------+
| id          | int           | NO   | PRI | NULL    | auto_increment |
| name        | varchar(255)  | NO   |     | NULL    |                |
| category    | varchar(255)  | NO   |     | NULL    |                |
| description | varchar(4096) | NO   |     | NULL    |                |
| address     | varchar(255)  | NO   |     | NULL    |                |
| transport   | varchar(4096) | NO   |     | NULL    |                |
| mrt         | varchar(255)  | YES  |     | NULL    |                |
| lat         | decimal(9,6)  | NO   |     | NULL    |                |
| lng         | decimal(9,6)  | NO   |     | NULL    |                |
+-------------+---------------+------+-----+---------+----------------+

mysql> desc image;
+------------------------+--------------+------+-----+---------+----------------+
| Field                  | Type         | Null | Key | Default | Extra          |
+------------------------+--------------+------+-----+---------+----------------+
| id                     | int          | NO   | PRI | NULL    | auto_increment |
| attraction_id          | int          | NO   |     | NULL    |                |
| image_no_of_attraction | int          | NO   |     | NULL    |                |
| url                    | varchar(255) | NO   |     | NULL    |                |
+------------------------+--------------+------+-----+---------+----------------+

ALTER TABLE image
ADD FOREIGN KEY (attraction_id) REFERENCES attraction(id);

mysql> SHOW CREATE TABLE attraction;
+------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| Table      | Create Table


                                                                                                       |
+------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| attraction | CREATE TABLE `attraction` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `category` varchar(255) NOT NULL,
  `description` varchar(4096) NOT NULL,
  `address` varchar(255) NOT NULL,
  `transport` varchar(4096) NOT NULL,
  `mrt` varchar(255) DEFAULT NULL,
  `lat` decimal(9,6) NOT NULL,
  `lng` decimal(9,6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=98 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci |
+------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
1 row in set (0.01 sec)

mysql> SHOW CREATE TABLE image;
+-------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| Table | Create Table


                                                   |
+-------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| image | CREATE TABLE `image` (
  `id` int NOT NULL AUTO_INCREMENT,
  `attraction_id` int NOT NULL,
  `image_no_of_attraction` int NOT NULL,
  `url` varchar(255) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `attraction_id` (`attraction_id`),
  CONSTRAINT `image_ibfk_1` FOREIGN KEY (`attraction_id`) REFERENCES `attraction` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=329 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci |
+-------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
1 row in set (0.00 sec)
"""

# Edited May 30 2024 for adding UNIQUE keys and using INSERT IGNORE to insert instead of INSERT:

"""
mysql> desc attraction;
+-------------+---------------+------+-----+---------+----------------+
| Field       | Type          | Null | Key | Default | Extra          |
+-------------+---------------+------+-----+---------+----------------+
| id          | int           | NO   | PRI | NULL    | auto_increment |
| name        | varchar(255)  | NO   | UNI | NULL    |                |
| category    | varchar(255)  | NO   |     | NULL    |                |
| description | varchar(4096) | NO   |     | NULL    |                |
| address     | varchar(255)  | NO   |     | NULL    |                |
| transport   | varchar(4096) | NO   |     | NULL    |                |
| mrt         | varchar(255)  | YES  |     | NULL    |                |
| lat         | decimal(9,6)  | NO   |     | NULL    |                |
| lng         | decimal(9,6)  | NO   |     | NULL    |                |
+-------------+---------------+------+-----+---------+----------------+
9 rows in set (0.00 sec)

mysql> SHOW CREATE TABLE attraction;
+------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| Table      | Create Table



             |
+------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| attraction | CREATE TABLE `attraction` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `category` varchar(255) NOT NULL,
  `description` varchar(4096) NOT NULL,
  `address` varchar(255) NOT NULL,
  `transport` varchar(4096) NOT NULL,
  `mrt` varchar(255) DEFAULT NULL,
  `lat` decimal(9,6) NOT NULL,
  `lng` decimal(9,6) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=61 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci |
+------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
1 row in set (0.00 sec)

mysql> desc image;
+------------------------+--------------+------+-----+---------+----------------+
| Field                  | Type         | Null | Key | Default | Extra          |
+------------------------+--------------+------+-----+---------+----------------+
| id                     | int          | NO   | PRI | NULL    | auto_increment |
| attraction_id          | int          | NO   | MUL | NULL    |                |
| image_no_of_attraction | int          | NO   |     | NULL    |                |
| url                    | varchar(255) | NO   | UNI | NULL    |                |
+------------------------+--------------+------+-----+---------+----------------+
4 rows in set (0.01 sec)

mysql> SHOW CREATE TABLE image;
+-------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| Table | Create Table


                                                                               |
+-------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| image | CREATE TABLE `image` (
  `id` int NOT NULL AUTO_INCREMENT,
  `attraction_id` int NOT NULL,
  `image_no_of_attraction` int NOT NULL,
  `url` varchar(255) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `url` (`url`),
  KEY `attraction_id` (`attraction_id`),
  CONSTRAINT `image_ibfk_1` FOREIGN KEY (`attraction_id`) REFERENCES `attraction` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=329 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci |
+-------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
1 row in set (0.00 sec)
"""

# MySQL Type text, json

# Use json to insert stuff into database
def load_json_into_json_ver_database():
  with open(file_path, "r", encoding="utf-8") as file:
      file_inputted = file.read()
      file_jsonloaded = json.loads(file_inputted)
      print(file_jsonloaded["result"]["results"][0])
      
      # connect to database
      website_db = mysql.connector.connect(
          host=db_host, user=db_user, password=db_pw, database=db_database)
      website_db_cursor = website_db.cursor()

      flag = False
      for item in file_jsonloaded["result"]["results"]:
      #     print(json.dumps(item))
            cmd = 'INSERT IGNORE INTO attraction_json (data) VALUES (%s)'
            website_db_cursor.execute(cmd, (json.dumps(item),))
            website_db.commit()

load_json_into_json_ver_database()
