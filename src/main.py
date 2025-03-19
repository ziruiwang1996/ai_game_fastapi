from fastapi import FastAPI
from .domains.roomba.endpoints import roomba_router
from .domains.gomoku.endpoints import gomoku_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="AI Game Hub API",
    description="API for managing multiple game domains",
    version="1.0.0"
)

origins = [
    "http://localhost:3000",  # React development server
    "http://127.0.0.1:3000"  # Alternative localhost format
     # Add your production frontend domain if applicable
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allows only specific origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allows all headers
)

app.include_router(roomba_router)
app.include_router(gomoku_router)