from fastapi import FastAPI, Depends, HTTPException, status, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
from datetime import timedelta
import uuid

from database import engine, Base, get_db
from models import User, Game
from auth import (
    verify_password, 
    get_password_hash, 
    create_access_token, 
    get_current_user,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from captcha import CaptchaManager

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")


class UserCreate(BaseModel):
    username: str
    password: str
    captcha_key: str
    captcha_code: str


class Token(BaseModel):
    access_token: str
    token_type: str


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


@app.get("/", response_class=HTMLResponse)
async def root():
    with open("static/index.html", "r", encoding="utf-8") as f:
        return f.read()


@app.get("/api/captcha")
async def get_captcha():
    captcha_text = CaptchaManager.generate_captcha_text()
    captcha_key = CaptchaManager.generate_captcha_key()
    
    CaptchaManager.store_captcha(captcha_key, captcha_text)
    
    image_buffer = CaptchaManager.generate_captcha_image(captcha_text)
    
    return StreamingResponse(
        image_buffer,
        media_type="image/png",
        headers={"X-Captcha-Key": captcha_key}
    )


@app.get("/api/captcha/new")
async def refresh_captcha():
    captcha_text = CaptchaManager.generate_captcha_text()
    captcha_key = CaptchaManager.generate_captcha_key()
    
    CaptchaManager.store_captcha(captcha_key, captcha_text)
    
    image_buffer = CaptchaManager.generate_captcha_image(captcha_text)
    
    return {
        "captcha_key": captcha_key,
        "captcha_image": f"/api/captcha?key={captcha_key}"
    }


@app.post("/api/register")
async def register(user: UserCreate, db: Session = Depends(get_db)):
    if not CaptchaManager.verify_captcha(user.captcha_key, user.captcha_code):
        raise HTTPException(status_code=400, detail="Invalid or expired captcha")
    
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    hashed_password = get_password_hash(user.password)
    new_user = User(username=user.username, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return {"message": "User created successfully", "username": new_user.username}


@app.post("/api/login", response_model=Token)
async def login(
    username: str = Form(...),
    password: str = Form(...),
    captcha_key: str = Form(...),
    captcha_code: str = Form(...),
    db: Session = Depends(get_db)
):
    if not CaptchaManager.verify_captcha(captcha_key, captcha_code):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired captcha",
        )
    
    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/api/game/start", response_model=StartGameResponse)
async def start_game(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    game_id = f"game_{uuid.uuid4()}"
    new_game = Game(
        game_id=game_id,
        owner_id=current_user.id,
        score=0,
        level=1
    )
    db.add(new_game)
    db.commit()
    db.refresh(new_game)
    
    return StartGameResponse(
        game_id=game_id,
        message="Game started!",
        score=0,
        level=1
    )


@app.post("/api/game/move", response_model=MoveResponse)
async def make_move(
    move_request: MoveRequest, 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    game = db.query(Game).filter(Game.game_id == move_request.game_id).first()
    
    if not game:
        return MoveResponse(
            game_id=move_request.game_id,
            direction=move_request.direction,
            score=0,
            level=1,
            message="Game not found! Please start a new game."
        )
    
    if game.owner_id != current_user.id:
        return MoveResponse(
            game_id=move_request.game_id,
            direction=move_request.direction,
            score=0,
            level=1,
            message="This is not your game!"
        )
    
    step = 50
    position = game.position.copy() if game.position else {"x": 125, "y": 125}
    
    if move_request.direction == "up":
        position["y"] = max(0, position["y"] - step)
    elif move_request.direction == "down":
        position["y"] = min(250, position["y"] + step)
    elif move_request.direction == "left":
        position["x"] = max(0, position["x"] - step)
    elif move_request.direction == "right":
        position["x"] = min(250, position["x"] + step)
    
    game.position = position
    game.score += 10
    if game.score % 100 == 0:
        game.level += 1
    
    db.commit()
    db.refresh(game)
    
    return MoveResponse(
        game_id=move_request.game_id,
        direction=move_request.direction,
        score=game.score,
        level=game.level,
        message=f"Moved {move_request.direction}! Score: {game.score}"
    )


@app.get("/api/game/status")
async def get_game_status(
    game_id: str, 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    game = db.query(Game).filter(Game.game_id == game_id).first()
    
    if not game:
        return {
            "game_id": game_id,
            "score": 0,
            "level": 1,
            "game_over": True,
            "message": "Game not found!"
        }
    
    if game.owner_id != current_user.id:
        return {
            "game_id": game_id,
            "score": 0,
            "level": 1,
            "game_over": True,
            "message": "This is not your game!"
        }
    
    return {
        "game_id": game.game_id,
        "score": game.score,
        "level": game.level,
        "game_over": game.game_over,
        "position": game.position
    }


@app.get("/api/user/games")
async def get_user_games(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    games = db.query(Game).filter(Game.owner_id == current_user.id).all()
    return {
        "games": [
            {
                "game_id": game.game_id,
                "score": game.score,
                "level": game.level,
                "created_at": game.created_at
            }
            for game in games
        ]
    }
