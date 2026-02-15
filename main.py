from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import uuid

app = FastAPI()

# Mount static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")

# Game data models
class GameState(BaseModel):
    game_id: str
    score: int
    level: int
    game_over: bool = False
    position: dict = {"x": 125, "y": 125}

class MoveRequest(BaseModel):
    game_id: str
    direction: str

class MoveResponse(BaseModel):
    game_id: str
    direction: str
    score: int
    level: int
    message: str

class StartGameResponse(BaseModel):
    game_id: str
    message: str
    score: int
    level: int

# In-memory game storage
games = {}

# Root endpoint that serves the game HTML page
@app.get("/", response_class=HTMLResponse)
async def root():
    with open("static/index.html", "r", encoding="utf-8") as f:
        return f.read()

# Game API endpoints
@app.get("/api/game/start", response_model=StartGameResponse)
async def start_game():
    """Start a new game"""
    game_id = f"game_{uuid.uuid4()}"
    games[game_id] = GameState(
        game_id=game_id,
        score=0,
        level=1
    )
    return StartGameResponse(
        game_id=game_id,
        message="Game started!",
        score=0,
        level=1
    )

@app.post("/api/game/move", response_model=MoveResponse)
async def make_move(move_request: MoveRequest):
    """Make a move in the game"""
    if move_request.game_id not in games:
        return MoveResponse(
            game_id=move_request.game_id,
            direction=move_request.direction,
            score=0,
            level=1,
            message="Game not found! Please start a new game."
        )
    
    game_id = move_request.game_id
    game = games[game_id]
    
    # Update position based on direction
    step = 50
    if move_request.direction == "up":
        game.position["y"] = max(0, game.position["y"] - step)
    elif move_request.direction == "down":
        game.position["y"] = min(250, game.position["y"] + step)
    elif move_request.direction == "left":
        game.position["x"] = max(0, game.position["x"] - step)
    elif move_request.direction == "right":
        game.position["x"] = min(250, game.position["x"] + step)
    
    # Update score and level
    game.score += 10
    if game.score % 100 == 0:
        game.level += 1
    
    return MoveResponse(
        game_id=game_id,
        direction=move_request.direction,
        score=game.score,
        level=game.level,
        message=f"Moved {move_request.direction}! Score: {game.score}"
    )

@app.get("/api/game/status")
async def get_game_status(game_id: str):
    """Get current game status"""
    if game_id not in games:
        return {
            "game_id": game_id,
            "score": 0,
            "level": 1,
            "game_over": True,
            "message": "Game not found!"
        }
    
    game = games[game_id]
    return {
        "game_id": game.game_id,
        "score": game.score,
        "level": game.level,
        "game_over": game.game_over,
        "position": game.position
    }
