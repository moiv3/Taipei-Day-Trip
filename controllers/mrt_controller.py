from fastapi import APIRouter
from models import mrt_model
from fastapi import Request

router = APIRouter(
    prefix="/api/mrts",
    tags=["MRT"]
)

# @router.get("/", summary="取得捷運站名稱列表", response_model=Data, tags=["MRT Station"], responses={500: {"model": Error}})
@router.get("/")
async def get_mrts(request: Request):
    return mrt_model.get_mrts()