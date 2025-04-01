from fastapi import APIRouter, HTTPException
from .logic import get_path
from starlette.responses import StreamingResponse

roomba_router = APIRouter(
    prefix="/api/roomba",
    tags=["roomba"]
)

@roomba_router.get("/")
async def get_animation(row:int, col:int, max_power:int):
    try:
        buffer = get_path(row, col, max_power)
        return StreamingResponse(buffer, media_type="image/gif")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error: {str(e)}")