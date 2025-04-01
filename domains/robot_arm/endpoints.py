from fastapi import APIRouter, HTTPException

robot_arm_router = APIRouter(
    prefix = "/api/robotarm",
    tag = ["robotarm"]
)

@robot_arm_router.get("/")
async def get():
    pass