import os
import datetime
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///cobalt.db')

engine = create_engine(DATABASE_URL, echo=False, connect_args={"check_same_thread": False} if DATABASE_URL.startswith('sqlite') else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class InterviewSession(Base):
    __tablename__ = 'sessions'
    id = Column(Integer, primary_key=True, index=True)
    role = Column(String, nullable=True)
    resume_data = Column(JSON)
    started_at = Column(DateTime, default=datetime.datetime.utcnow)
    qas = relationship('QAEntry', back_populates='session')


class QAEntry(Base):
    __tablename__ = 'qas'
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey('sessions.id'))
    question = Column(Text)
    answer = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    session = relationship('InterviewSession', back_populates='qas')


def init_db():
    Base.metadata.create_all(bind=engine)
