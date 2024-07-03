# https://github.com/ViktorViskov/fastapi-mvc/

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import RequestValidationError
from utils.pydantic_base_models import Error
import traceback

from controllers import user_controller
from controllers import mrt_controller
from controllers import attraction_controller
from controllers import booking_controller
from controllers import order_controller

app = FastAPI()

# Static Files
app.mount("/static", StaticFiles(directory="static"), name="static")

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

app.include_router(user_controller.router)
app.include_router(mrt_controller.router)
app.include_router(attraction_controller.router)
app.include_router(booking_controller.router)
app.include_router(order_controller.router)


# 這段通常怎麼用MVC拆分?
# exception handlers for 422 and 500
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: Exception):    
    traceback.print_exc()
    return JSONResponse(status_code=400, content=(Error(error="true", message="格式不正確，請確認輸入資訊").dict()))

@app.exception_handler(500)
async def internal_server_error_handler(request: Request, exc: Exception):
    traceback.print_exc()
    return JSONResponse(status_code=500, content=(Error(error="true", message="伺服器內部異常，請聯繫管理員確認").dict()))