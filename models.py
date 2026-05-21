from sqlalchemy import Column, Integer, String
from database import Base

class Recipe(Base):
    __tablename__ = "recipes"

    id = Column(Integer, primary_key=True, index=True)
    label = Column(String, nullable=False)
    source = Column(String, nullable=False)
    url = Column(String, nullable=False)
