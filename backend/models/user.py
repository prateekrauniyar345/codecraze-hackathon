from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func
from database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    oauth_id = Column(String(255), unique=True, nullable=False, index=True)
    oauth_provider = Column(String(50), nullable=False) # 'google', 'auth0', etc.
    full_name = Column(String(255))
    email = Column(String(255), unique=True, nullable=False, index=True)
    # picture = Column(Text, nullable=True) 
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_login = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<User(id={self.id})>"