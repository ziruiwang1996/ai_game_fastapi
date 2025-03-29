from fastapi import APIRouter, HTTPException
from .models import GomokuDomain
from .logic import minimax
import numpy as np
import base64

gomoku_router = APIRouter(
    prefix="/api/gomoku",
    tags=["gomoku"]
)

TIE = 0
PLAYER_WIN = 1
AI_WIN = 2
IN_PROGRESS = 3

# serialize numpy.ndarray to base64 string
def numpy_to_base64(arr: np.ndarray) -> str:
    byte_data = arr.astype(np.int32).tobytes()
    return base64.b64encode(byte_data).decode('utf-8')

# deserialize base64 string back to numpy.ndarray
def base64_to_numpy(base64_str: str, shape: tuple, dtype: type = np.int32) -> np.ndarray:
    byte_data = base64.b64decode(base64_str)  # Decode base64 string to bytes
    return np.frombuffer(byte_data, dtype=dtype).reshape(shape)  # Convert bytes back to ndarray

@gomoku_router.get("/start")
async def start_game(board_size:int, win_size:int, ai_first:bool):
    try:
        game = GomokuDomain(board_size, win_size)
        state = game.initial_state()
        if ai_first:
            state, _ = minimax(game, state, max_depth=5)
        return {"state": numpy_to_base64(state), "status": IN_PROGRESS}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error: {str(e)}")

@gomoku_router.get("/move")
async def get_game_state(board_size:int, win_size:int, col:int, row:int, state_str: str):
    try:
        game = GomokuDomain(board_size, win_size)
        state = base64_to_numpy(state_str, shape=(board_size, board_size))

        state = game.perform((row, col), state)
        if game.is_over_in(state):
            if game.is_draw(state):
                return {"state": numpy_to_base64(state), "status": TIE}
            return {"state": numpy_to_base64(state), "status": PLAYER_WIN}
        
        state, _ = minimax(game, state, max_depth=5)
        if game.is_over_in(state):
            if game.is_draw(state):
                return {"state": numpy_to_base64(state), "status": TIE}
            return {"state": numpy_to_base64(state), "status": AI_WIN}
        
        return {"state": numpy_to_base64(state), "status": IN_PROGRESS}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error: {str(e)}")