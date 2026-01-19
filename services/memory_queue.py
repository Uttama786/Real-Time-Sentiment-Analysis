"""
In-Memory Queue Service - Alternative to Redis for Windows development
"""
import json
import logging
from typing import Dict, List, Optional
from threading import Lock
from collections import deque
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class InMemoryQueue:
    """Thread-safe in-memory queue implementation"""
    
    def __init__(self, max_size: int = 10000):
        """Initialize in-memory queue"""
        self.queue = deque(maxlen=max_size)
        self.lock = Lock()
        self.max_size = max_size
        logger.info(f"InMemoryQueue initialized (max_size={max_size})")
    
    def lpush(self, name: str, item: str) -> int:
        """Push item to left of queue (returns queue size)"""
        with self.lock:
            try:
                self.queue.appendleft(item)
                return len(self.queue)
            except Exception as e:
                logger.error(f"Error pushing to queue: {e}")
                return -1
    
    def rpop(self, name: str, timeout: int = 0) -> Optional[str]:
        """Pop item from right of queue"""
        with self.lock:
            try:
                if len(self.queue) > 0:
                    return self.queue.pop()
                return None
            except Exception as e:
                logger.error(f"Error popping from queue: {e}")
                return None
    
    def llen(self, name: str) -> int:
        """Get queue length"""
        with self.lock:
            return len(self.queue)
    
    def lrange(self, name: str, start: int, end: int) -> List[str]:
        """Get range of items from queue"""
        with self.lock:
            items = list(self.queue)
            return items[start:end+1] if end >= 0 else items[start:]
    
    def clear(self, name: str) -> None:
        """Clear queue"""
        with self.lock:
            self.queue.clear()
            logger.info("Queue cleared")
    
    def flush(self) -> None:
        """Flush queue"""
        self.clear("")
    
    def get(self, name: str) -> Optional[str]:
        """Get item from queue (alias for rpop)"""
        return self.rpop(name)
    
    def set(self, key: str, value: str, ex: int = None) -> bool:
        """Set key-value (for compatibility)"""
        return True


class QueueManager:
    """Manages in-memory queue for distributed tasks"""
    
    def __init__(self):
        """Initialize queue manager"""
        self.queue = InMemoryQueue()
        self.stats = {
            'total_processed': 0,
            'total_errors': 0,
            'started_at': datetime.utcnow().isoformat()
        }
        logger.info("QueueManager initialized")
    
    def enqueue(self, data: Dict) -> bool:
        """Enqueue task"""
        try:
            json_str = json.dumps(data)
            result = self.queue.lpush('sentiment_queue', json_str)
            logger.debug(f"Enqueued task: {data.get('id', 'unknown')}")
            return result > 0
        except Exception as e:
            logger.error(f"Error enqueuing task: {e}")
            self.stats['total_errors'] += 1
            return False
    
    def dequeue(self) -> Optional[Dict]:
        """Dequeue task"""
        try:
            item = self.queue.rpop('sentiment_queue')
            if item:
                return json.loads(item)
            return None
        except Exception as e:
            logger.error(f"Error dequeuing task: {e}")
            self.stats['total_errors'] += 1
            return None
    
    def get_stats(self) -> Dict:
        """Get queue statistics"""
        self.stats['queue_size'] = self.queue.llen('sentiment_queue')
        return self.stats
    
    def increment_processed(self) -> None:
        """Increment processed count"""
        self.stats['total_processed'] += 1


# Global queue manager instance
_queue_manager = None


def get_queue_manager() -> QueueManager:
    """Get or create global queue manager"""
    global _queue_manager
    if _queue_manager is None:
        _queue_manager = QueueManager()
    return _queue_manager


def get_redis_client():
    """
    Get Redis client (fallback to in-memory queue for Windows)
    This maintains compatibility with existing Redis code
    """
    return get_queue_manager().queue


if __name__ == "__main__":
    # Test the queue
    logger.info("Testing InMemoryQueue...")
    
    manager = get_queue_manager()
    
    # Enqueue some data
    test_data = [
        {'id': 1, 'text': 'Great product!', 'source': 'test'},
        {'id': 2, 'text': 'Not bad', 'source': 'test'},
        {'id': 3, 'text': 'Horrible!', 'source': 'test'},
    ]
    
    for data in test_data:
        manager.enqueue(data)
    
    logger.info(f"Stats: {manager.get_stats()}")
    
    # Dequeue and process
    while True:
        item = manager.dequeue()
        if not item:
            break
        logger.info(f"Dequeued: {item}")
        manager.increment_processed()
    
    logger.info(f"Final stats: {manager.get_stats()}")
