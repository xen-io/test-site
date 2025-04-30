from sqlalchemy import Column, String, Boolean, Integer, UUID
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'users'

    id = Column(UUID, primary_key=True)
    email = Column(String(100), unique=True, nullable=False)
    username = Column(String(100), unique=True, nullable=False)
    password = Column(String(255), nullable=False)

    access_level = Column(Integer, default=1)
    is_admin = Column(Boolean, default=False)
    is_verified = Column(Boolean, default=False)
