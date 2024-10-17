# app/schemas.py

from pydantic import BaseModel, validator, Field
from datetime import datetime, date, time, timezone
from typing import Optional, Union
import pytz
import phonenumbers


class ScheduleCallRequest(BaseModel):
    user_phone_number: str = Field(..., description="User's phone number")
    call_time: Union[int, datetime] = Field(...,
                                            description="Call time in ISO 8601 format")
    persona: str = Field(..., description="Persona for the call")
    scenario: str = Field(..., description="Scenario for the call")
    custom_description: str = Field(...,
                                    description="Custom description for the call")

    @validator('call_time')
    def validate_call_time(cls, v):
        if isinstance(v, int):
            return datetime.utcfromtimestamp(v)
        return v

    @validator('user_phone_number')
    def validate_phone_number(cls, v):
        # Add any phone number validation logic here
        if not v:
            raise ValueError("Phone number cannot be empty")
        return v

    @validator('persona', 'scenario')
    def validate_non_empty_string(cls, v):
        if not v.strip():
            raise ValueError("Field cannot be empty")
        return v


class ScheduleCallResponse(BaseModel):
    message: str
    scheduled_time: datetime
    call_id: int


class UserCreate(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None
