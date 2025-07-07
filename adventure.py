from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from DB import SessionLocal
from PydanticModels import AdventureModel, AdventureCreate
from DB import Adventure
from utils import get_db
from typing import List
router = APIRouter()

@router.post("/adventures/", response_model=AdventureModel)
def create_adventure(adventure: AdventureCreate, db: Session = Depends(get_db)):
    db_adventure = Adventure(**adventure.dict())
    db.add(db_adventure)
    db.commit()
    db.refresh(db_adventure)
    return db_adventure

@router.put("/adventures/{adventure_id}", response_model=AdventureModel)
def update_adventure(adventure_id: int, adventure: AdventureModel, db: Session = Depends(get_db)):
    db_adventure = db.query(Adventure).filter(Adventure.id == adventure_id).first()
    if not db_adventure:
        raise HTTPException(status_code=404, detail="Adventure not found")
    for key, value in adventure.dict().items():
        setattr(db_adventure, key, value)
    db.commit()
    return db_adventure

@router.delete("/adventures/{adventure_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_adventure(adventure_id: int, db: Session = Depends(get_db)):
    db_adventure = db.query(Adventure).filter(Adventure.id == adventure_id).first()
    if not db_adventure:
        raise HTTPException(status_code=404, detail="Adventure not found")
    db.delete(db_adventure)
    db.commit()
    return {"message": "Adventure deleted"}

@router.get("/adventures/", response_model=List[AdventureModel])
def read_adventures(db: Session = Depends(get_db)):
    return db.query(Adventure).all()
