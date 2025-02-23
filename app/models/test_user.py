from . import Base
from sqlalchemy import Column, String, TIMESTAMP, func, text

class TestUser(Base):
    __tablename__ = 'test_user'
    
    email = Column(String, unique=True, nullable=True)
    room_name = Column(String, nullable=True)
    
    # Audit timestamps
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
