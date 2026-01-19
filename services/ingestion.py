"""
Data ingestion service - collects data from multiple sources
"""
import os
import time
import yaml
import json
import logging
import feedparser
from datetime import datetime
from typing import List, Dict
from dotenv import load_dotenv
import sys

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.memory_queue import get_redis_client
from services.social_media_api import TwitterAPIClient

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DataIngestionService:
    """Service for ingesting data from multiple sources"""
    
    def __init__(self, config_path='config/sources.yaml'):
        """Initialize ingestion service"""
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
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
        
        # Initialize social media API clients (Twitter only)
        try:
            self.twitter_client = TwitterAPIClient(self.config['sources']['twitter'])
            logger.info("Twitter API client initialized")
        except Exception as e:
            logger.warning(f"Could not initialize Twitter client: {e}")
            self.twitter_client = None
        
        logger.info("Data Ingestion Service initialized")
    
    def push_to_queue(self, data: Dict):
        """Push data to Redis queue"""
        try:
            self.redis_client.lpush(self.queue_name, json.dumps(data))
            logger.debug(f"Pushed data to queue: {data.get('source', 'unknown')}")
        except Exception as e:
            logger.error(f"Error pushing to queue: {e}")
    
    def ingest_from_twitter(self):
        """Ingest data from Twitter API"""
        twitter_config = self.config['sources']['twitter']
        
        if not twitter_config['enabled']:
            logger.info("Twitter ingestion is disabled")
            return
        
        logger.info("Ingesting from Twitter...")
        
        if not self.twitter_client:
            logger.warning("Twitter client not initialized, skipping")
            return
        
        # Get search keywords from config
        keywords = twitter_config.get('keywords', [])
        max_tweets = twitter_config.get('max_tweets', 50)
        max_replies_per_tweet = twitter_config.get('max_replies_per_tweet', 50)
        fetch_replies = twitter_config.get('fetch_replies', True)
        
        total_tweets = 0
        total_replies = 0
        
        for keyword in keywords:
            try:
                logger.info(f"Searching Twitter for: {keyword}")
                tweets = self.twitter_client.search_tweets(keyword, max_results=max_tweets)
                
                for tweet in tweets:
                    # Push the original tweet
                    data = {
                        'source': 'twitter',
                        'text': tweet['text'],
                        'timestamp': tweet['created_at'],
                        'metadata': json.dumps({
                            'tweet_id': tweet['id'],
                            'user': tweet.get('author_username', 'unknown'),
                            'author_name': tweet.get('author_name', 'Unknown'),
                            'keyword': keyword
                        })
                    }
                    self.push_to_queue(data)
                    total_tweets += 1
                    
                    # Fetch replies if enabled
                    if fetch_replies and self.twitter_client:
                        try:
                            # Get conversation_id from tweet (use tweet_id if not available)
                            conversation_id = tweet.get('conversation_id', tweet['id'])
                            replies = self.twitter_client.get_tweet_replies(
                                tweet_id=tweet['id'],
                                conversation_id=conversation_id,
                                max_replies=max_replies_per_tweet
                            )
                            
                            # Push each reply to queue
                            for reply in replies:
                                reply_data = {
                                    'source': 'twitter_reply',
                                    'text': reply['text'],
                                    'timestamp': reply['created_at'],
                                    'metadata': json.dumps({
                                        'reply_id': reply['id'],
                                        'tweet_id': tweet['id'],
                                        'conversation_id': reply.get('conversation_id', tweet['id']),
                                        'user': reply.get('author_username', 'unknown'),
                                        'author_name': reply.get('author_name', 'Unknown'),
                                        'keyword': keyword
                                    })
                                }
                                self.push_to_queue(reply_data)
                                total_replies += 1
                            
                            if replies:
                                logger.info(f"Retrieved {len(replies)} replies for tweet {tweet['id']}")
                                
                        except Exception as e:
                            logger.error(f"Error fetching replies for tweet {tweet['id']}: {e}")
                
                logger.info(f"Retrieved {len(tweets)} tweets for keyword: {keyword}")
                
            except Exception as e:
                logger.error(f"Error fetching tweets for keyword '{keyword}': {e}")
        
        logger.info(f"Ingested {total_tweets} tweets and {total_replies} replies total")
    
    def ingest_from_news(self):
        """Ingest data from RSS news feeds"""
        news_config = self.config['sources']['news']
        
        if not news_config['enabled']:
            logger.info("News ingestion is disabled")
            return
        
        logger.info("Ingesting from news feeds...")
        total_articles = 0
        
        for feed_url in news_config['feeds']:
            try:
                feed = feedparser.parse(feed_url)
                logger.info(f"Fetching from {feed_url}")
                
                for entry in feed.entries[:10]:  # Limit to 10 per feed
                    # Extract text from title and description
                    text = f"{entry.get('title', '')} {entry.get('summary', '')}"
                    
                    data = {
                        'source': 'news',
                        'text': text,
                        'timestamp': datetime.utcnow().isoformat(),
                        'metadata': json.dumps({
                            'title': entry.get('title', ''),
                            'link': entry.get('link', ''),
                            'published': entry.get('published', '')
                        })
                    }
                    self.push_to_queue(data)
                    total_articles += 1
                
            except Exception as e:
                logger.error(f"Error fetching feed {feed_url}: {e}")
        
        logger.info(f"Ingested {total_articles} news articles")
    
    def ingest_from_custom(self):
        """Ingest from custom API endpoint"""
        custom_config = self.config['sources']['custom']
        
        if not custom_config['enabled']:
            logger.info("Custom ingestion is disabled")
            return
        
        # Placeholder for custom API integration
        logger.info("Custom ingestion not implemented yet")
    
    def run_ingestion_cycle(self):
        """Run one complete ingestion cycle"""
        logger.info("Starting ingestion cycle...")
        
        try:
            self.ingest_from_twitter()
            self.ingest_from_news()
            self.ingest_from_custom()
            logger.info("Ingestion cycle completed")
        except Exception as e:
            logger.error(f"Error during ingestion cycle: {e}")
    
    def run(self):
        """Main run loop"""
        logger.info("Starting Data Ingestion Service...")
        
        # Get polling intervals
        twitter_interval = self.config['sources']['twitter'].get('polling_interval', 60)
        news_interval = self.config['sources']['news'].get('polling_interval', 300)
        
        # Use the minimum interval for the main loop
        min_interval = min(twitter_interval, news_interval)
        
        cycle_count = 0
        
        while True:
            try:
                self.run_ingestion_cycle()
                cycle_count += 1
                logger.info(f"Completed {cycle_count} cycles. Sleeping for {min_interval}s...")
                time.sleep(min_interval)
            except KeyboardInterrupt:
                logger.info("Shutting down ingestion service...")
                break
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                time.sleep(10)  # Wait before retrying


if __name__ == "__main__":
    service = DataIngestionService()
    service.run()
