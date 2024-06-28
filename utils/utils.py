from fastapi import Header
from passlib.context import CryptContext
from utils.pydantic_base_models import TokenOut
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# 這個感覺不太好分類，可以問一下
def get_token_header(authorization: str = Header(...)) -> TokenOut:
    stripped_token = authorization[len("Bearer "):]
    if not stripped_token:
        return False
    return TokenOut(token=stripped_token)

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