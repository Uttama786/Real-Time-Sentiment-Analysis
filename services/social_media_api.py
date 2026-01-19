"""
Real-time Twitter API Integration
Extracts tweets for sentiment analysis
"""
import os
import sys
import logging
import yaml
from datetime import datetime
from typing import List, Dict

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

logger = logging.getLogger(__name__)


class TwitterAPIClient:
    """Twitter API client for extracting real-time tweets"""
    
    def __init__(self, config: dict):
        """Initialize Twitter API client"""
        self.config = config
        self.client = None
        
        try:
            import tweepy
            
            # Check if using Bearer Token (Twitter API v2)
            if config.get('use_bearer_token', True) and config.get('bearer_token'):
                bearer_token = os.getenv('TWITTER_BEARER_TOKEN', config.get('bearer_token'))
                if bearer_token and bearer_token != 'YOUR_TWITTER_BEARER_TOKEN_HERE':
                    self.client = tweepy.Client(bearer_token=bearer_token)
                    logger.info("Twitter API v2 client initialized with Bearer Token")
                else:
                    logger.warning("Twitter Bearer Token not configured")
            else:
                # Use OAuth 1.0a (API v1.1)
                api_key = os.getenv('TWITTER_API_KEY', config.get('api_key'))
                api_secret = os.getenv('TWITTER_API_SECRET', config.get('api_secret'))
                access_token = os.getenv('TWITTER_ACCESS_TOKEN', config.get('access_token'))
                access_token_secret = os.getenv('TWITTER_ACCESS_TOKEN_SECRET', config.get('access_token_secret'))
                
                if all([api_key, api_secret, access_token, access_token_secret]) and \
                   api_key != 'YOUR_TWITTER_API_KEY_HERE':
                    self.client = tweepy.Client(
                        consumer_key=api_key,
                        consumer_secret=api_secret,
                        access_token=access_token,
                        access_token_secret=access_token_secret
                    )
                    logger.info("Twitter API v1.1 client initialized with OAuth")
                else:
                    logger.warning("Twitter OAuth credentials not configured")
                    
        except ImportError:
            logger.warning("tweepy not installed. Install with: pip install tweepy")
        except Exception as e:
            logger.error(f"Error initializing Twitter client: {e}")
    
    def search_tweets(self, query: str, max_results: int = 50) -> List[Dict]:
        """
        Search for tweets using Twitter API
        
        Args:
            query: Search query
            max_results: Maximum number of tweets to return
            
        Returns:
            List of tweet dictionaries
        """
        if not self.client:
            logger.warning("Twitter client not initialized - using sample data")
            return self._get_sample_tweets(query)
        
        try:
            # Search recent tweets using API v2
            response = self.client.search_recent_tweets(
                query=query,
                max_results=min(max_results, 100),  # API limit
                tweet_fields=['created_at', 'author_id', 'lang', 'public_metrics', 'conversation_id'],
                expansions=['author_id'],
                user_fields=['username', 'name']
            )
            
            tweets = []
            if response.data:
                # Create user lookup
                users = {user.id: user for user in response.includes.get('users', [])}
                
                for tweet in response.data:
                    author = users.get(tweet.author_id)
                    tweets.append({
                        'id': tweet.id,
                        'text': tweet.text,
                        'created_at': tweet.created_at.isoformat(),
                        'author_id': tweet.author_id,
                        'author_username': author.username if author else 'unknown',
                        'author_name': author.name if author else 'Unknown',
                        'lang': tweet.lang,
                        'retweet_count': tweet.public_metrics.get('retweet_count', 0),
                        'like_count': tweet.public_metrics.get('like_count', 0),
                        'conversation_id': getattr(tweet, 'conversation_id', tweet.id),
                        'source': 'twitter'
                    })
            
            logger.info(f"Retrieved {len(tweets)} tweets for query: {query}")
            return tweets
            
        except Exception as e:
            logger.error(f"Error fetching tweets: {e}")
            return self._get_sample_tweets(query)
    
    def get_tweet_replies(self, tweet_id: str, conversation_id: str = None, max_replies: int = 50) -> List[Dict]:
        """
        Get replies to a specific tweet
        
        Args:
            tweet_id: The tweet ID to get replies for
            conversation_id: The conversation ID (if available, more efficient)
            max_replies: Maximum number of replies to return
            
        Returns:
            List of reply tweet dictionaries
        """
        if not self.client:
            logger.warning("Twitter client not initialized - using sample replies")
            return self._get_sample_replies(tweet_id)
        
        try:
            # Use conversation_id if available, otherwise search for replies
            search_query = f"conversation_id:{conversation_id or tweet_id}"
            
            response = self.client.search_recent_tweets(
                query=search_query,
                max_results=min(max_replies, 100),  # API limit
                tweet_fields=['created_at', 'author_id', 'lang', 'public_metrics', 'in_reply_to_user_id'],
                expansions=['author_id'],
                user_fields=['username', 'name']
            )
            
            replies = []
            if response.data:
                # Create user lookup
                users = {user.id: user for user in response.includes.get('users', [])}
                
                for reply in response.data:
                    # Skip the original tweet itself
                    if reply.id == tweet_id:
                        continue
                    
                    author = users.get(reply.author_id)
                    replies.append({
                        'id': reply.id,
                        'text': reply.text,
                        'created_at': reply.created_at.isoformat(),
                        'author_id': reply.author_id,
                        'author_username': author.username if author else 'unknown',
                        'author_name': author.name if author else 'Unknown',
                        'lang': reply.lang,
                        'retweet_count': reply.public_metrics.get('retweet_count', 0),
                        'like_count': reply.public_metrics.get('like_count', 0),
                        'in_reply_to_tweet_id': tweet_id,
                        'conversation_id': conversation_id or tweet_id,
                        'source': 'twitter_reply'
                    })
            
            logger.info(f"Retrieved {len(replies)} replies for tweet {tweet_id}")
            return replies
            
        except Exception as e:
            logger.error(f"Error fetching replies for tweet {tweet_id}: {e}")
            return self._get_sample_replies(tweet_id)
    
    def _get_sample_replies(self, tweet_id: str) -> List[Dict]:
        """Return sample replies for testing"""
        samples = [
            "I totally agree with this!",
            "This is not accurate at all.",
            "Interesting perspective, thanks for sharing.",
            "I had a similar experience.",
            "Could you provide more details?",
        ]
        
        return [{
            'id': f'reply_{tweet_id}_{i}',
            'text': text,
            'created_at': datetime.utcnow().isoformat(),
            'author_id': f'reply_user_{i}',
            'author_username': f'replyuser{i}',
            'author_name': f'Reply User {i}',
            'lang': 'en',
            'retweet_count': 0,
            'like_count': 0,
            'in_reply_to_tweet_id': tweet_id,
            'conversation_id': tweet_id,
            'source': 'twitter_reply_sample'
        } for i, text in enumerate(samples)]
    
    def _get_sample_tweets(self, query: str) -> List[Dict]:
        """Return sample tweets for testing"""
        samples = [
            f"Just tried this {query} and it's amazing! Highly recommend it!",
            f"Disappointed with the {query}. Not worth the price.",
            f"The {query} is okay, nothing special but does the job.",
            f"Love the new {query}! Best purchase this year!",
            f"Terrible experience with {query}. Customer service was awful.",
        ]
        
        return [{
            'id': f'sample_{i}',
            'text': text,
            'created_at': datetime.utcnow().isoformat(),
            'author_id': f'user_{i}',
            'author_username': f'user{i}',
            'author_name': f'User {i}',
            'lang': 'en',
            'retweet_count': 0,
            'like_count': 0,
            'source': 'twitter_sample'
        } for i, text in enumerate(samples)]


def test_apis():
    """Test Twitter API connection"""
    print("\n" + "="*60)
    print("Testing Social Media API Connections")
    print("="*60 + "\n")
    
    # Load configuration
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'sources.yaml')
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    print("🐦 Testing Twitter API...")
    twitter_config = config['sources'].get('twitter', {})
    twitter_client = TwitterAPIClient(twitter_config)
    
    if twitter_client.client:
        tweets = twitter_client.search_tweets("product review", max_results=10)
        print(f"✅ Twitter: Retrieved {len(tweets)} tweets")
        if tweets:
            print(f"   Sample: {tweets[0]['text'][:60]}...")
    else:
        print("⚠️  Twitter: Using sample data (API not configured)")
        tweets = twitter_client.search_tweets("product", max_results=5)
        print(f"   Sample data: {len(tweets)} tweets")
    
    print("\n" + "="*60)
    print("API Test Complete")
    print("="*60 + "\n")


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    test_apis()
