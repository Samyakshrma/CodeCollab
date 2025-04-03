# Real-Time Code Collaboration API

## Overview
This is a **real-time collaborative coding API** built with FastAPI and WebSockets. It allows multiple users to collaboratively edit code in real time using WebSockets and Redis for pub/sub message distribution.

## Features
- **User Authentication** (Register/Login) with JWT tokens
- **WebSocket-based real-time collaboration**
- **Redis-based Pub/Sub** to sync live code changes
- **Secure WebSocket connections** using JWT authentication
- **Persistence of code sessions** in a database

## Tech Stack
- **FastAPI** (Python Web Framework)
- **WebSockets** (Real-time communication)
- **Redis** (Pub/Sub for real-time updates)
- **SQLAlchemy** (ORM for database interactions)
- **OAuth2 & JWT** (User authentication & authorization)

## Installation & Setup
### 1. Clone the Repository
```bash
git clone https://github.com/your-repo/realtime-code-collab.git
cd realtime-code-collab
```

### 2. Install Dependencies
Ensure you have Python installed (3.8+ recommended). Then, install the required dependencies:
```bash
pip install fastapi[all] sqlalchemy redis pydantic jose uvicorn
```

### 3. Setup Redis
Make sure you have Redis installed and running locally.
```bash
redis-server
```

### 4. Setup Database
Create and configure your database. Modify `database.py` accordingly.
```python
# Example connection URL
DATABASE_URL = "sqlite:///./test.db"  # Use PostgreSQL/MySQL as needed
```
Then, initialize the database using SQLAlchemy models.

### 5. Run the API Server
Start the FastAPI server:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## API Endpoints

### 1. **User Authentication**
#### Register a new user
```http
POST /register/
```
**Request Body:**
```json
{
  "username": "testuser",
  "password": "securepassword"
}
```

#### Login and get access token
```http
POST /token
```
**Request Body:**
```json
{
  "username": "testuser",
  "password": "securepassword"
}
```
**Response:**
```json
{
  "access_token": "<JWT_TOKEN>",
  "token_type": "bearer"
}
```

### 2. **WebSocket Collaboration**
#### Connect to a collaborative session
```ws
ws://localhost:8000/ws/{session_id}?token=<JWT_TOKEN>
```
- Each session ID is unique.
- Messages are broadcasted to all connected users in the session.
- Messages are stored using Redis pub/sub.

#### WebSocket Message Format
```json
{
  "user": "testuser",
  "content": "Updated code..."
}
```

## Project Structure
```
realtime-code-collab/
│── main.py               # Main FastAPI application
│── database.py           # Database setup (SQLAlchemy)
│── models.py             # ORM models (User, CodeSession)
│── auth.py               # Authentication utilities (JWT, hashing)
│── requirements.txt      # Python dependencies
└── README.md             # Project documentation
```

## Contribution
Contributions are welcome! Feel free to submit pull requests or open issues.

## License
MIT License.

