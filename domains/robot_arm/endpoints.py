from fastapi import APIRouter, HTTPException
from .logic import adjust_robot_arm
from starlette.responses import StreamingResponse

robot_arm_router = APIRouter(
    prefix = "/api/robotarm",
    tags = ["robotarm"]
)

@robot_arm_router.get("/")
async def get(arms: str, target: str):
    try:
        arms = [float(char.lstrip().rstrip()) for char in arms.split(',')]
        target = [float(char.lstrip().rstrip()) for char in target.split(',')]
        buffer = adjust_robot_arm(arms, target)
        return StreamingResponse(buffer, media_type="image/gif")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error: {str(e)}")