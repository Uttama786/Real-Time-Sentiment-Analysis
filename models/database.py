"""
Database models for sentiment analysis system
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

Base = declarative_base()


class SentimentRecord(Base):
    """Model for storing sentiment analysis results"""
    __tablename__ = 'sentiment_records'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    source = Column(String(50), nullable=False)  # twitter, news, custom
    text = Column(Text, nullable=False)
    sentiment = Column(String(20), nullable=False)  # positive, negative, neutral
    score = Column(Float, nullable=False)  # -1 to 1
    confidence = Column(Float, nullable=False)  # 0 to 1
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    meta_data = Column(Text, nullable=True)  # JSON string for additional data
    
    def __repr__(self):
        return f"<SentimentRecord(id={self.id}, sentiment={self.sentiment}, score={self.score})>"
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'source': self.source,
            'text': self.text,
            'sentiment': self.sentiment,
            'score': self.score,
            'confidence': self.confidence,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'metadata': self.meta_data
        }


class DataSource(Base):
    """Model for tracking data sources"""
    __tablename__ = 'data_sources'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), unique=True, nullable=False)
    status = Column(String(20), default='active')  # active, inactive, error
    last_fetch = Column(DateTime, nullable=True)
    total_records = Column(Integer, default=0)
    error_count = Column(Integer, default=0)
    
    def __repr__(self):
        return f"<DataSource(name={self.name}, status={self.status})>"


# Database connection
def get_database_url():
    """Construct database URL from environment variables"""
    db_host = os.getenv('DB_HOST', 'localhost')
    db_port = os.getenv('DB_PORT', '5432')
    db_name = os.getenv('DB_NAME', 'sentiment_db')
    db_user = os.getenv('DB_USER', 'postgres')
    db_password = os.getenv('DB_PASSWORD', '')
    
    return f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"


def init_database():
    """Initialize database and create tables"""
    engine = create_engine(get_database_url())
    Base.metadata.create_all(engine)
    return engine


def get_session():
    """Create a new database session"""
    engine = create_engine(get_database_url())
    Session = sessionmaker(bind=engine)
    return Session()
