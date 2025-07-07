from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse
from DB import SessionLocal, Base, Adventure
import jwt
from utils import pwd_context
from typing import List

from PydanticModels import UserBase, UserCreate, UserGet,UserAdventureModel

from  DB import User
from utils import get_db, create_access_token, decode_token, hash_password

router = APIRouter()
 

@router.post("/register", response_model=UserBase)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    hashed_password = hash_password(user.password)
    db_user = User(username=user.username, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.post("/login")
def login(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if not db_user or not pwd_context.verify(user.password, db_user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    token = create_access_token({"sub": db_user.username})
    response = JSONResponse(content={"message": "Login successful"})
    response.set_cookie(key="access_token", value=token, httponly=False)
    return response
@router.get("/me", response_model=UserGet)
def get_user_info(request: Request, db: Session = Depends(get_db)):
    username = decode_token(request)
    db_user = db.query(User).filter(User.username == username).first()

    if not db_user:
        raise HTTPException(status_code=404, detail="User not found") 
     
    adventures = [UserAdventureModel.from_orm(adventure) for adventure in db_user.adventures]
    completed_adventures = [UserAdventureModel.from_orm(adventure) for adventure in db_user.adventures if adventure.current_topic_index==0]

 
    total_adventures = db.query(Adventure).count()
    completed_adventures_count = len(completed_adventures)
    progress_percentage = (completed_adventures_count / total_adventures * 100) if total_adventures > 0 else 0.0

 
    user_data = UserGet(
        id=db_user.id,
        username=db_user.username,
        adventures=adventures,
        completed_adventures=completed_adventures,
        rating=db_user.rating,
        total_adventures=total_adventures,
        completed_adventures_count=completed_adventures_count,
        progress_percentage=progress_percentage
    )

    return user_data


@router.get("/rating", response_model=List[UserGet])
def get_all_players(db: Session = Depends(get_db)): 
    users = db.query(User).order_by(User.rating.desc()).all()
     
    players = [UserGet.from_orm(user) for user in users]
    
    return players
