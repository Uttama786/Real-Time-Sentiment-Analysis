"""
Processing service - analyzes sentiment from queued data
"""
import os
import sys
import time
import json
import logging
from datetime import datetime
from dotenv import load_dotenv

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.sentiment_model import SentimentAnalyzer
from models.preprocessor import TextPreprocessor
from services.storage import StorageService
from services.memory_queue import get_redis_client

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ProcessingService:
    """Service for processing and analyzing sentiment"""
    
    def __init__(self):
        """Initialize processing service"""
        # Initialize Redis/Queue client (uses in-memory queue on Windows)
        try:
            import redis
            redis_host = os.getenv('REDIS_HOST', 'localhost')
            redis_port = int(os.getenv('REDIS_PORT', 6379))
            self.redis_client = redis.Redis(
                host=redis_host,
                port=redis_port,
                decode_responses=True
            )
            logger.info("Using Redis for queue")
        except Exception as e:
            logger.warning(f"Redis not available, using in-memory queue: {e}")
            self.redis_client = get_redis_client()
        
        # Test Redis connection
        try:
            self.redis_client.ping()
            logger.info("Redis connection successful")
        except Exception as e:
            logger.warning(f"Redis not available, switching to in-memory queue: {e}")
            self.redis_client = get_redis_client()
        self.queue_name = 'sentiment_queue'
        
        # Initialize sentiment analyzer and preprocessor
        self.analyzer = SentimentAnalyzer()
        self.preprocessor = TextPreprocessor()
        
        # Initialize storage service
        self.storage = StorageService()
        
        # Processing stats
        self.processed_count = 0
        self.error_count = 0
        
        logger.info("Processing Service initialized")
    
    def get_queue_size(self):
        """Get current queue size"""
        return self.redis_client.llen(self.queue_name)
    
    def process_item(self, item_data: dict):
        """Process a single item from the queue"""
        try:
            text = item_data.get('text', '')
            source = item_data.get('source', 'unknown')
            
            if not text:
                logger.warning("Empty text received, skipping")
                return
            
            # Preprocess text
            processed_text = self.preprocessor.preprocess(text)
            
            if not processed_text:
                logger.warning(f"Text too short after preprocessing: {text[:50]}")
                return
            
            # Analyze sentiment
            analysis_result = self.analyzer.analyze(processed_text)
            
            # Prepare record for storage
            record = {
                'source': source,
                'text': text,
                'sentiment': analysis_result['sentiment'],
                'score': analysis_result['score'],
                'confidence': analysis_result['confidence'],
                'timestamp': item_data.get('timestamp', datetime.utcnow().isoformat()),
                'metadata': item_data.get('metadata', '{}')
            }
            
            # Store in database
            self.storage.save_sentiment(record)
            
            self.processed_count += 1
            
            if self.processed_count % 10 == 0:
                logger.info(f"Processed {self.processed_count} items (Errors: {self.error_count})")
            
        except Exception as e:
            self.error_count += 1
            logger.error(f"Error processing item: {e}")
    
    def process_batch(self, batch_size=10):
        """Process a batch of items from the queue"""
        processed = 0
        
        for _ in range(batch_size):
            try:
                # Pop item from queue (blocking with timeout)
                item = self.redis_client.brpop(self.queue_name, timeout=1)
                
                if item is None:
                    break  # Queue is empty
                
                # Parse JSON data
                _, item_json = item
                item_data = json.loads(item_json)
                
                # Process the item
                self.process_item(item_data)
                processed += 1
                
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON in queue: {e}")
                self.error_count += 1
            except Exception as e:
                logger.error(f"Error in batch processing: {e}")
                self.error_count += 1
        
        return processed
    
    def run(self):
        """Main run loop"""
        logger.info("Starting Processing Service...")
        
        batch_size = int(os.getenv('BATCH_SIZE', 50))
        processing_interval = int(os.getenv('PROCESSING_INTERVAL', 5))
        
        while True:
            try:
                queue_size = self.get_queue_size()
                
                if queue_size > 0:
                    logger.info(f"Queue size: {queue_size}. Processing batch...")
                    processed = self.process_batch(batch_size)
                    
                    if processed > 0:
                        logger.info(f"Processed {processed} items")
                else:
                    logger.debug("Queue is empty, waiting...")
                
                time.sleep(processing_interval)
                
            except KeyboardInterrupt:
                logger.info("Shutting down processing service...")
                break
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                time.sleep(10)  # Wait before retrying
        
        # Print final stats
        logger.info(f"Final stats - Processed: {self.processed_count}, Errors: {self.error_count}")


if __name__ == "__main__":
    service = ProcessingService()
    service.run()
