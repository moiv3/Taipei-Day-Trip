# https://github.com/ViktorViskov/fastapi-mvc/

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from controllers import user_controller
from controllers import mrt_controller
from controllers import attraction_controller
from controllers import booking_controller

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