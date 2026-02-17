from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, JSON, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    games = relationship("Game", back_populates="owner")


class Game(Base):
    __tablename__ = "games"
    
    id = Column(Integer, primary_key=True, index=True)
    game_id = Column(String, unique=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    score = Column(Integer, default=0)
    level = Column(Integer, default=1)
    game_over = Column(Boolean, default=False)
    position = Column(JSON, default={"x": 125, "y": 125})
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    owner = relationship("User", back_populates="games")
