# AI Game Center Backend Server 

App Demo: http://3.12.182.165
AI Game Suite is a collection of interactive games that showcase various AI algorithms and concepts. Each game is designed to be both educational and entertaining, allowing users to explore AI-driven problem-solving techniques in a fun and engaging way.

## Features

- **Roomba Cleaning Simulation**: Test an A* search algorithm as Roomba navigates a messy room, avoiding obstacles and managing power efficiently.
- **Gomoku**: Play the classic Gomoku game with an AI opponent.
- **Cat and Mouse**: Simulate a chase scenario where a cat tries to catch a mouse in a grid-based environment.
- **Robot Arm Challenge**: Explore gradient descent optimization as a robotic arm adjusts its joints to reach a target.

## Technologies Used

- **Frontend**: React.js, JavaScript
- **Backend**: FastAPI, Python
- **Containerization**: Docker, Docker Compose
- **Web Server**: Nginx

## Prerequisites

- [Docker](https://www.docker.com/) installed on your machine.
- [Docker Compose](https://docs.docker.com/compose/) installed.

## How to Run the Application

1. **Clone the Repository**:
   ```bash
   mkdir ai-game
   cd ai-game
   git clone https://github.com/ziruiwang1996/ai_game_fastapi.git 
   git clone https://github.com/ziruiwang1996/ai_game_react.git 
   mv ai_game_fastapi backend
   mv ai_game_react frontend
   # add docker-compose.yml showing below
   docker-compose up -d #run
   ```

   ```
   version: '3'
   services:
      fastapi:
         build: 
               context: ./back-end/src
               dockerfile: Dockerfile
         ports:
               - "8000:8000"
         networks:
               - ai-game-network
      nginx:
         build: 
               context: ./front-end
               dockerfile: Dockerfile
         container_name: nginx_proxy
         ports:
               - "80:80"
         depends_on:
               - fastapi
         networks:
               - ai-game-network
   networks:
      ai-game-network:
         driver: bridge