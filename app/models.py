from sqlalchemy import Column, Integer, String, DateTime
from .database import Base
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class ScheduledCall(Base):
    __tablename__ = "scheduled_calls"

    id = Column(Integer, primary_key=True, index=True)
    user_phone_number = Column(String, nullable=False)
    call_time = Column(DateTime, nullable=False)
    persona = Column(String, nullable=False)
    scenario = Column(String, nullable=False)
    custom_description = Column(String)
    status = Column(String, default="Scheduled")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
