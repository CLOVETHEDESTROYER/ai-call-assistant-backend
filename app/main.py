# app/main.py

import threading
from pathlib import Path
from pydantic import BaseModel, Field, validator
from .models import User
import pytz
from datetime import timedelta, datetime, date, time
from fastapi.security import OAuth2PasswordRequestForm
from app.dependencies import get_db, get_current_active_user
from app.auth import get_password_hash, authenticate_user, create_access_token, status
import warnings
import logging
from fastapi import FastAPI, HTTPException, Depends, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from app.schemas import ScheduleCallRequest, ScheduleCallResponse, UserCreate, Token
from app.models import ScheduledCall, User
from app.database import SessionLocal, engine, Base
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
import os
from dotenv import load_dotenv
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.date import DateTrigger
from twilio.rest import Client
from openai import OpenAI
import websocket
import json
from twilio.twiml.voice_response import VoiceResponse, Connect, Say, Stream
from .services.realtime_service import handle_media_stream, make_call

# from urllib3.exceptions import NotOpenSSLWarning


# Suppress NotOpenSSLWarning (optional)
# warnings.simplefilter('ignore', NotOpenSSLWarning)

# Load environment variables from .env file
load_dotenv()

# Initialize FastAPI app
app = FastAPI()

# Allow CORS for frontend access (modify origins as needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update with your frontend's origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create all database tables
Base.metadata.create_all(bind=engine)

# Initialize Twilio client

# Initialize OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Initialize APScheduler
scheduler = BackgroundScheduler()
scheduler.start()


# Authentication Constants
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Dependency to get DB session


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Initialize the Realtime API
# realtime_api = RealtimeAPI(api_key=OPENAI_API_KEY)

# Start the WebSocket connection in a separate thread
# threading.Thread(target=realtime_api.start_connection).start()

# WebSocket connection setup

# Create a WebSocket app


# Function to make a call via Twilio

class ScheduleCallRequest(BaseModel):
    user_phone_number: str
    call_time: int  # Use datetime type for better validation
    persona: str
    scenario: str
    custom_description: str = None  # New field for custom scenario description

    @validator('call_time')
    def validate_call_time(cls, v):
        # Convert timestamp to datetime
        return datetime.fromtimestamp(v)


class ScheduleCallResponse(BaseModel):
    call_id: int
    status: str


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Replace print statements with logger


@app.get("/", response_class=HTMLResponse)
async def index_page():
    return {"message": "Twilio Media Stream Server is running!"}


@app.post("/incoming-call")
async def handle_incoming_call(request: Request):
    """Handle incoming call and return TwiML response to connect to Media Stream."""
    response = VoiceResponse()
    response.say(
        "Please wait while we connect your call to the AI voice assistant.")
    response.pause(length=1)
    response.say("OK, you can start talking!")

    # Get the scenario and custom_description from the request query parameters
    scenario = request.query_params.get("scenario", "")
    custom_description = request.query_params.get("custom_description", "")

    host = request.url.hostname
    connect = Connect()
    connect.stream(
        url=f'wss://{host}/media-stream?scenario={scenario}&custom_description={custom_description}')
    response.append(connect)
    return HTMLResponse(content=str(response), media_type="application/xml")


@app.websocket("/media-stream")
async def media_stream_endpoint(websocket: WebSocket):
    scenario = websocket.query_params.get("scenario", "")
    custom_description = websocket.query_params.get("custom_description", "")
    await handle_media_stream(websocket, scenario, custom_description)


@app.post("/schedule-call")
async def schedule_call(request: ScheduleCallRequest, db: Session = Depends(get_db)):
    try:
        logger.info(f"Received schedule call request: {request}")

        call_time_utc = request.call_time.astimezone(pytz.UTC)

        # Create a new ScheduledCall record
        new_call = ScheduledCall(
            user_phone_number=request.user_phone_number,
            call_time=call_time_utc,
            persona=request.persona,
            scenario=request.scenario,
            custom_description=request.custom_description,
            status="Scheduled"
        )
        db.add(new_call)
        db.commit()
        db.refresh(new_call)

        # Schedule the call using APScheduler
        scheduler.add_job(
            make_call,
            trigger=DateTrigger(run_date=call_time_utc),
            args=[request.user_phone_number,
                  request.scenario, request.custom_description]
        )

        logger.info(f"Call scheduled successfully for {call_time_utc}")
        return {"message": "Call scheduled successfully", "scheduled_time": call_time_utc}

    except ValueError as e:
        logger.error(f"Invalid data: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Invalid data: {str(e)}")
    except SQLAlchemyError as e:
        logger.error(f"Database error: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error occurred")
    except Exception as e:
        logger.error(f"Unexpected error in schedule_call: {str(e)}")
        logger.exception("Detailed traceback:")
        raise HTTPException(
            status_code=500, detail="An unexpected error occurred")


@app.get("/call-status/{call_id}", response_model=ScheduleCallResponse)
def call_status(call_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    call = db.query(ScheduledCall).filter(ScheduledCall.id == call_id).first()
    if not call:
        raise HTTPException(status_code=404, detail="Call not found")
    return ScheduleCallResponse(call_id=call.id, status=call.status)


@app.post("/register", response_model=Token)
def register(user: UserCreate, db: Session = Depends(get_db)):
    try:
        db_user = db.query(User).filter(User.username == user.username).first()
        if db_user:
            raise HTTPException(
                status_code=400, detail="Username already registered")
        hashed_password = get_password_hash(user.password)
        new_user = User(username=user.username,
                        hashed_password=hashed_password)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": new_user.username}, expires_delta=access_token_expires
        )
        return {"access_token": access_token, "token_type": "bearer"}
    except Exception as e:
        logger.error(f"Error registering user: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@app.post("/token", response_model=Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    try:
        user = authenticate_user(db, form_data.username, form_data.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.username}, expires_delta=access_token_expires
        )
        return {"access_token": access_token, "token_type": "bearer"}
    except Exception as e:
        logger.error(f"Error during login: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@app.get("/protected")
def protected_route(current_user: User = Depends(get_current_active_user)):
    return {"message": f"Hello, {current_user.username}. This is a protected endpoint."}


@app.websocket("/ws/calls")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            print(f"Received from client: {data}")
            # Process the received data and generate a response
            response = f"Echo: {data}"  # Replace with AI response logic
            await websocket.send_text(response)
    except WebSocketDisconnect:
        print("Client disconnected")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 5050)))
