"""
Storage service - handles database operations
"""
import os
import sys
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.database import SentimentRecord, DataSource, get_session, init_database
from sqlalchemy import func, and_

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class StorageService:
    """Service for database operations"""
    
    def __init__(self):
        """Initialize storage service"""
        try:
            init_database()
            logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
    
    def save_sentiment(self, record_data: Dict) -> Optional[int]:
        """
        Save sentiment record to database
        
        Args:
            record_data: Dictionary containing record fields
            
        Returns:
            Record ID if successful, None otherwise
        """
        session = get_session()
        
        try:
            record = SentimentRecord(
                source=record_data['source'],
                text=record_data['text'],
                sentiment=record_data['sentiment'],
                score=record_data['score'],
                confidence=record_data['confidence'],
                timestamp=datetime.fromisoformat(record_data['timestamp']) 
                           if isinstance(record_data['timestamp'], str) 
                           else record_data['timestamp'],
                meta_data=record_data.get('metadata', '{}')
            )
            
            session.add(record)
            session.commit()
            
            record_id = record.id
            session.close()
            
            logger.debug(f"Saved record {record_id}")
            return record_id
            
        except Exception as e:
            logger.error(f"Error saving sentiment record: {e}")
            session.rollback()
            session.close()
            return None
    
    def get_recent_sentiments(self, limit: int = 100) -> List[Dict]:
        """Get recent sentiment records"""
        session = get_session()
        
        try:
            records = session.query(SentimentRecord)\
                .order_by(SentimentRecord.timestamp.desc())\
                .limit(limit)\
                .all()
            
            result = [record.to_dict() for record in records]
            session.close()
            return result
            
        except Exception as e:
            logger.error(f"Error fetching recent sentiments: {e}")
            session.close()
            return []
    
    def get_sentiment_stats(self, hours: int = 24) -> Dict:
        """
        Get sentiment statistics for the specified time range
        
        Args:
            hours: Number of hours to look back
            
        Returns:
            Statistics dictionary
        """
        session = get_session()
        
        try:
            # Calculate time threshold
            time_threshold = datetime.utcnow() - timedelta(hours=hours)
            
            # Get counts by sentiment
            sentiment_counts = session.query(
                SentimentRecord.sentiment,
                func.count(SentimentRecord.id).label('count')
            ).filter(
                SentimentRecord.timestamp >= time_threshold
            ).group_by(
                SentimentRecord.sentiment
            ).all()
            
            # Get average scores
            avg_score = session.query(
                func.avg(SentimentRecord.score).label('avg_score')
            ).filter(
                SentimentRecord.timestamp >= time_threshold
            ).scalar()
            
            # Get total count
            total_count = session.query(
                func.count(SentimentRecord.id)
            ).filter(
                SentimentRecord.timestamp >= time_threshold
            ).scalar()
            
            # Get counts by source
            source_counts = session.query(
                SentimentRecord.source,
                func.count(SentimentRecord.id).label('count')
            ).filter(
                SentimentRecord.timestamp >= time_threshold
            ).group_by(
                SentimentRecord.source
            ).all()
            
            session.close()
            
            return {
                'total_records': total_count or 0,
                'average_score': round(float(avg_score or 0), 4),
                'sentiment_distribution': {
                    sentiment: count for sentiment, count in sentiment_counts
                },
                'source_distribution': {
                    source: count for source, count in source_counts
                },
                'time_range_hours': hours
            }
            
        except Exception as e:
            logger.error(f"Error calculating stats: {e}")
            session.close()
            return {}
    
    def get_historical_data(self, start_date: datetime, end_date: datetime) -> List[Dict]:
        """Get historical sentiment data"""
        session = get_session()
        
        try:
            records = session.query(SentimentRecord)\
                .filter(
                    and_(
                        SentimentRecord.timestamp >= start_date,
                        SentimentRecord.timestamp <= end_date
                    )
                )\
                .order_by(SentimentRecord.timestamp)\
                .all()
            
            result = [record.to_dict() for record in records]
            session.close()
            return result
            
        except Exception as e:
            logger.error(f"Error fetching historical data: {e}")
            session.close()
            return []
    
    def update_data_source_status(self, source_name: str, status: str, error: bool = False):
        """Update data source tracking information"""
        session = get_session()
        
        try:
            source = session.query(DataSource)\
                .filter(DataSource.name == source_name)\
                .first()
            
            if not source:
                source = DataSource(name=source_name)
                session.add(source)
            
            source.status = status
            source.last_fetch = datetime.utcnow()
            
            if error:
                source.error_count = (source.error_count or 0) + 1
            else:
                source.total_records = (source.total_records or 0) + 1
            
            session.commit()
            session.close()
            
        except Exception as e:
            logger.error(f"Error updating data source: {e}")
            session.rollback()
            session.close()


if __name__ == "__main__":
    # Test storage service
    storage = StorageService()
    
    # Test saving a record
    test_record = {
        'source': 'test',
        'text': 'This is a test message',
        'sentiment': 'positive',
        'score': 0.75,
        'confidence': 0.85,
        'timestamp': datetime.utcnow().isoformat(),
        'metadata': '{}'
    }
    
    record_id = storage.save_sentiment(test_record)
    print(f"Saved record with ID: {record_id}")
    
    # Test getting stats
    stats = storage.get_sentiment_stats(24)
    print(f"Stats: {stats}")
