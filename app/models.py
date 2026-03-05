import os
import datetime
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, JSON, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///cobalt.db')

# Render (and Heroku) provide postgres:// URLs but SQLAlchemy requires postgresql://
if DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

_is_sqlite = DATABASE_URL.startswith('sqlite')

_engine_kwargs = dict(echo=False)
if _is_sqlite:
    _engine_kwargs['connect_args'] = {"check_same_thread": False}
else:
    _engine_kwargs['pool_size'] = 5
    _engine_kwargs['max_overflow'] = 10
    _engine_kwargs['pool_pre_ping'] = True

engine = create_engine(DATABASE_URL, **_engine_kwargs)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class InterviewSession(Base):
    __tablename__ = 'interview_sessions'
    id = Column(Integer, primary_key=True, index=True)
    role = Column(String, nullable=True)
    resume_data = Column(JSON)
    started_at = Column(DateTime, default=datetime.datetime.utcnow)
    qas = relationship('QAEntry', back_populates='session', cascade='all, delete-orphan')


class QAEntry(Base):
    __tablename__ = 'qa_entries'
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey('interview_sessions.id'))
    question = Column(Text)
    answer = Column(Text)
    score = Column(Float, default=0.0)
    feedback = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    session = relationship('InterviewSession', back_populates='qas')


def init_db():
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
