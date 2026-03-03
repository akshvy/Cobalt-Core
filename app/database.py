from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from .config import settings

engine = create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    sessions = relationship("Session", back_populates="user")


class Session(Base):
    __tablename__ = "sessions"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    role = Column(String, index=True)
    resume_text = Column(Text)
    score = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    user = relationship("User", back_populates="sessions")
    interactions = relationship("Interaction", back_populates="session")


class Interaction(Base):
    __tablename__ = "interactions"
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id"))
    question = Column(Text)
    user_answer = Column(Text)
    ai_feedback = Column(Text)
    transcript = Column(Text, nullable=True)  # for video mode
    score = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    session = relationship("Session", back_populates="interactions")


class Feedback(Base):
    __tablename__ = "feedback"
    id = Column(Integer, primary_key=True, index=True)
    interaction_id = Column(Integer, ForeignKey("interactions.id"))
    repeated_words = Column(Text)  # JSON
    grammar_issues = Column(Text)  # JSON
    filler_words = Column(Text)  # JSON
    vocabulary_score = Column(Float)
    clarity_score = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)


Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
