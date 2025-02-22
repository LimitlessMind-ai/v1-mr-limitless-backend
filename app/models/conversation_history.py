from . import Base
from sqlalchemy import Column, String, TIMESTAMP, func

class RentinvestoUser(Base):
    __tablename__ = 'rentinveso_user'
    __table_args__ = {'extend_existing': True}
    
    user_id = Column(String, primary_key=True)
    
    # New columns
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    verified_age = Column(String, nullable=True)
    unverified_age = Column(String, nullable=True)
    gender = Column(String, nullable=True)  # Will store "male" or "female"
    language = Column(String, nullable=True)
    country = Column(String, nullable=True)
    city = Column(String, nullable=True)
    platform = Column(String, nullable=False)  # Will store either "app" or "web"
    room_name = Column(String, nullable=True)
    
    # Audit timestamps
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
