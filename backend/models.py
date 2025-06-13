from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base  # Assuming you have a database.py with Base defined

class SpyCat(Base):
    """
    SQLAlchemy model representing a Spy Cat in the system.

    Attributes:
        id (int): Primary key, auto-incremented
        name (str): Name of the spy cat (required)
        years_of_experience (int): Years of spy experience (required)
        breed (str): Cat breed (validated against TheCatAPI)
        salary (float): Monthly salary in USD (must be positive)
        mission_id (int): Foreign key to current mission (optional)
        mission (relationship): Relationship to Mission model
    """
    __tablename__ = "spy_cats"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    years_of_experience = Column(Integer, nullable=False)
    breed = Column(String, nullable=False)
    salary = Column(Float, nullable=False)
    
    # Relationship to Mission (one cat can have one active mission)
    mission_id = Column(Integer, ForeignKey("missions.id"), nullable=True)
    mission = relationship("Mission", back_populates="cat")

    def __repr__(self):
        return f"<SpyCat {self.name} (ID: {self.id})>"


class Mission(Base):
    """
    SQLAlchemy model representing a spy mission.

    Attributes:
        id (int): Primary key, auto-incremented
        is_completed (bool): Mission completion status (default False)
        cat_id (int): Foreign key to assigned spy cat (optional)
        cat (relationship): Relationship to SpyCat model
        targets (relationship): One-to-many relationship with Target model
    """
    __tablename__ = "missions"

    id = Column(Integer, primary_key=True, index=True)
    is_completed = Column(Boolean, default=False)
    
    # Relationship to SpyCat (one mission can have one assigned cat)
    cat_id = Column(Integer, ForeignKey("spy_cats.id"), nullable=True)
    cat = relationship("SpyCat", back_populates="mission")
    
    # One mission can have multiple targets (1-3)
    targets = relationship("Target", back_populates="mission", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Mission {self.id} (Completed: {self.is_completed})>"


class Target(Base):
    """
    SQLAlchemy model representing a mission target.

    Attributes:
        id (int): Primary key, auto-incremented
        name (str): Target name (required)
        country (str): Target country (required)
        notes (str): Spy notes about the target (default empty string)
        is_completed (bool): Target completion status (default False)
        mission_id (int): Foreign key to parent mission (required)
        mission (relationship): Relationship to Mission model
    """
    __tablename__ = "targets"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    country = Column(String, nullable=False)
    notes = Column(String, default="")
    is_completed = Column(Boolean, default=False)
    
    # Relationship to Mission (many targets belong to one mission)
    mission_id = Column(Integer, ForeignKey("missions.id"))
    mission = relationship("Mission", back_populates="targets")

    def __repr__(self):
        return f"<Target {self.name} (Completed: {self.is_completed})>"