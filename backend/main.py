from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, conint, confloat
from typing import List, Optional
import requests
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from .models import SpyCat, Mission, Target
from .database import Base, SessionLocal

# Database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./sca.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# SQLAlchemy models
class SpyCatDB(Base):
    __tablename__ = "spy_cats"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    years_of_experience = Column(Integer, nullable=False)
    breed = Column(String, nullable=False)
    salary = Column(Float, nullable=False)
    mission_id = Column(Integer, ForeignKey("missions.id"), nullable=True)

class MissionDB(Base):
    __tablename__ = "missions"
    id = Column(Integer, primary_key=True, index=True)
    is_completed = Column(Boolean, default=False)
    cat_id = Column(Integer, ForeignKey("spy_cats.id"), nullable=True)
    targets = relationship("TargetDB", back_populates="mission")

class TargetDB(Base):
    __tablename__ = "targets"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    country = Column(String, nullable=False)
    notes = Column(String, default="")
    is_completed = Column(Boolean, default=False)
    mission_id = Column(Integer, ForeignKey("missions.id"))
    mission = relationship("MissionDB", back_populates="targets")

Base.metadata.create_all(bind=engine)

# Pydantic models
class SpyCatBase(BaseModel):
    name: str
    years_of_experience: conint(ge=0)
    breed: str
    salary: confloat(gt=0)

class SpyCatCreate(SpyCatBase):
    pass

class SpyCat(SpyCatBase):
    id: int

    class Config:
        orm_mode = True

class TargetBase(BaseModel):
    name: str
    country: str

class TargetCreate(TargetBase):
    pass

class Target(TargetBase):
    id: int
    notes: str
    is_completed: bool

    class Config:
        orm_mode = True

class MissionBase(BaseModel):
    cat_id: Optional[int] = None
    targets: List[TargetCreate]

class MissionCreate(MissionBase):
    pass

class Mission(MissionBase):
    id: int
    is_completed: bool
    targets: List[Target]

    class Config:
        orm_mode = True

class TargetUpdate(BaseModel):
    notes: Optional[str] = None
    is_completed: Optional[bool] = None

# FastAPI app
app = FastAPI()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Breed validation with TheCatAPI
def validate_breed(breed: str):
    response = requests.get("https://api.thecatapi.com/v1/breeds")
    breeds = [b["name"].lower() for b in response.json()]
    if breed.lower() not in breeds:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid breed. Valid breeds: {', '.join(breeds[:5])}...",
        )

# Spy Cats endpoints
@app.post("/cats/", response_model=SpyCat)
def create_cat(cat: SpyCatCreate, db: Session = Depends(get_db)):
    validate_breed(cat.breed)
    db_cat = SpyCatDB(**cat.dict())
    db.add(db_cat)
    db.commit()
    db.refresh(db_cat)
    return db_cat

@app.get("/cats/", response_model=List[SpyCat])
def read_cats(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(SpyCatDB).offset(skip).limit(limit).all()

@app.get("/cats/{cat_id}", response_model=SpyCat)
def read_cat(cat_id: int, db: Session = Depends(get_db)):
    db_cat = db.query(SpyCatDB).filter(SpyCatDB.id == cat_id).first()
    if not db_cat:
        raise HTTPException(status_code=404, detail="Cat not found")
    return db_cat

@app.put("/cats/{cat_id}", response_model=SpyCat)
def update_cat_salary(cat_id: int, salary: float, db: Session = Depends(get_db)):
    db_cat = db.query(SpyCatDB).filter(SpyCatDB.id == cat_id).first()
    if not db_cat:
        raise HTTPException(status_code=404, detail="Cat not found")
    db_cat.salary = salary
    db.commit()
    db.refresh(db_cat)
    return db_cat

@app.delete("/cats/{cat_id}")
def delete_cat(cat_id: int, db: Session = Depends(get_db)):
    db_cat = db.query(SpyCatDB).filter(SpyCatDB.id == cat_id).first()
    if not db_cat:
        raise HTTPException(status_code=404, detail="Cat not found")
    
    # Check if cat is on a mission
    if db_cat.mission_id:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete cat assigned to a mission"
        )
    
    db.delete(db_cat)
    db.commit()
    return {"message": "Cat deleted successfully"}

# Missions endpoints
@app.post("/missions/", response_model=Mission)
def create_mission(mission: MissionCreate, db: Session = Depends(get_db)):
    # Validate targets count
    if len(mission.targets) < 1 or len(mission.targets) > 3:
        raise HTTPException(
            status_code=400,
            detail="Mission must have 1-3 targets"
        )
    
    # Validate cat exists if provided
    if mission.cat_id:
        db_cat = db.query(SpyCatDB).filter(SpyCatDB.id == mission.cat_id).first()
        if not db_cat:
            raise HTTPException(status_code=404, detail="Cat not found")
    
    db_mission = MissionDB(
        is_completed=False,
        cat_id=mission.cat_id
    )
    db.add(db_mission)
    db.commit()
    db.refresh(db_mission)
    
    # Create targets
    for target in mission.targets:
        db_target = TargetDB(
            **target.dict(),
            mission_id=db_mission.id
        )
        db.add(db_target)
    
    db.commit()
    db.refresh(db_mission)
    return db_mission

@app.put("/targets/{target_id}")
def update_target(target_id: int, update: TargetUpdate, db: Session = Depends(get_db)):
    db_target = db.query(TargetDB).filter(TargetDB.id == target_id).first()
    if not db_target:
        raise HTTPException(status_code=404, detail="Target not found")
    
    # Check if mission is completed
    if db_target.mission.is_completed:
        raise HTTPException(
            status_code=400,
            detail="Cannot update target in completed mission"
        )
    
    # Check if target is completed and trying to update notes
    if db_target.is_completed and update.notes is not None:
        raise HTTPException(
            status_code=400,
            detail="Cannot update notes for completed target"
        )
    
    if update.notes is not None:
        db_target.notes = update.notes
    if update.is_completed is not None:
        db_target.is_completed = update.is_completed
        
        # Check if all targets are completed
        mission = db_target.mission
        all_completed = all(t.is_completed for t in mission.targets)
        if all_completed:
            mission.is_completed = True
    
    db.commit()
    return {"message": "Target updated successfully"}