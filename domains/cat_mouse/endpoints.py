from fastapi import APIRouter, HTTPException
from .logic import TD_Q_Learning
from .models import CatMouseDomain
from starlette.responses import StreamingResponse

catmouse_router = APIRouter(
    prefix="/api/catmouse",
    tags=["catmouse"]
)

@catmouse_router.get("/")
async def get_animation(row:int, col:int):
    try:
        game = CatMouseDomain(row, col)
        buffer = TD_Q_Learning(game)
        return StreamingResponse(buffer, media_type="image/gif")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error: {str(e)}")