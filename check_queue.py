import sys
sys.path.insert(0, '.')
from services.memory_queue import get_redis_client

r = get_redis_client()
queue_len = r.llen('sentiment_queue')
print(f"Queue length: {queue_len}")
print(f"Queue has {'items waiting' if queue_len > 0 else 'NO items - ingestion/processor may not be running'}")
