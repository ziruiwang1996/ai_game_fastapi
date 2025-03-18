from fastapi import APIRouter
from .logic import get_path
from starlette.responses import StreamingResponse

router = APIRouter(
    prefix="/roomba",
    tags=["roomba"]
)

@router.get("/{row}&{col}&{max_power}")
async def get_animation(row:int, col:int, max_power:int):
    buffer = get_path(row, col, max_power)
    return StreamingResponse(buffer, media_type="image/gif")