from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
import redis.asyncio as redis  # Use async Redis
import json
import uuid
import asyncio
from collections import defaultdict
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from jose import jwt, JWTError

from database import get_db
from models import User, CodeSession
from auth import hash_password, verify_password, create_access_token

app = FastAPI()

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for testing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Async Redis for Pub/Sub
redis_client = redis.Redis(host="localhost", port=6379, decode_responses=True)

# Store active WebSocket connections
active_connections = defaultdict(set)

SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"

async def verify_token(token: str, db: Session):
    """ Verifies JWT token and returns the user """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user = db.query(User).filter(User.username == payload["sub"]).first()
        if not user:
            raise ValueError("Invalid token")
        return user
    except JWTError:
        raise WebSocketDisconnect()

@app.websocket("/ws/{session_id}")
async def websocket_endpoint(
    websocket: WebSocket, 
    session_id: str, 
    token: str = Query(...),  # Token passed as query param
    db: Session = Depends(get_db)
):
    """ WebSocket connection with authentication and real-time updates """
    user = await verify_token(token, db)
    await websocket.accept()

    active_connections[session_id].add(websocket)

    # Load existing code and send to the user
    session = db.query(CodeSession).filter(CodeSession.session_id == session_id).first()
    if session:
        await websocket.send_text(session.content)

    # Start Redis subscriber
    asyncio.create_task(redis_subscriber(session_id))

    try:
        while True:
            message = await websocket.receive_text()
            await redis_client.publish(session_id, json.dumps({"user": user.username, "content": message}))

    except WebSocketDisconnect:
        active_connections[session_id].discard(websocket)
        if not active_connections[session_id]:  
            del active_connections[session_id]

async def redis_subscriber(session_id: str):
    """ Listen for Redis messages and send updates to WebSocket clients """
    pubsub = redis_client.pubsub()
    await pubsub.subscribe(session_id)

    while True:
        message = await pubsub.get_message(ignore_subscribe_messages=True)
        if message:
            data = json.loads(message["data"])
            if session_id in active_connections:
                for ws in active_connections[session_id].copy():
                    try:
                        await ws.send_text(json.dumps(data))
                    except:
                        active_connections[session_id].discard(ws)
        await asyncio.sleep(0.01)  # Prevents CPU overload

# ✅ User Registration
class RegisterRequest(BaseModel):
    username: str
    password: str

@app.post("/register/")
def register(user_data: RegisterRequest, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")

    new_user = User(
        id=str(uuid.uuid4()),  
        username=user_data.username,
        password_hash=hash_password(user_data.password)
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "User registered successfully", "user_id": new_user.id}

# ✅ User Login (Generate Token)
@app.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

# ✅ Get Current User
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")

    return user
