from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.sql import func

from utils.database import Base


class Token(Base):
    __tablename__ = 'tokens'

    id = Column(Integer, primary_key=True, autoincrement=True)
    token = Column(String(255), nullable=False, unique=True, index=True)
    is_error = Column(Boolean, default=False)
    is_refresh_token = Column(Boolean, default=False)
    timestamp = Column(Integer, default=0)
    created_at = Column(DateTime, default=func.now())
    created_by = Column(Integer, ForeignKey('users.id'))
    description = Column(String(255), nullable=False)
