from sqlalchemy import Column, String, Text
from database import Base

class CodeSession(Base):
    __tablename__ = "code_sessions"

    session_id = Column(String, primary_key=True, index=True)
    content = Column(Text, default="")


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password_hash = Column(String)