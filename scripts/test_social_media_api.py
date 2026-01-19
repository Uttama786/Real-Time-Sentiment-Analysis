"""
Test script for Twitter API integration
"""
import os
import sys
import yaml
from dotenv import load_dotenv

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.social_media_api import TwitterAPIClient

load_dotenv()


def test_twitter():
    """Test Twitter API connection"""
    print("\n" + "="*60)
    print("🐦 TWITTER API TEST")
    print("="*60)
    
    # Load config
    with open('config/sources.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    twitter_config = config['sources']['twitter']
    
    # Check if enabled
    if not twitter_config.get('enabled'):
        print("⚠️  Twitter is DISABLED in sources.yaml")
        print("   Enable it by setting 'enabled: true' in config/sources.yaml")
        return False
    
    # Check credentials
    bearer_token = os.getenv('TWITTER_BEARER_TOKEN')
    api_key = os.getenv('TWITTER_API_KEY')
    
    if not bearer_token and not api_key:
        print("❌ No Twitter credentials found in .env file")
        print("   Add TWITTER_BEARER_TOKEN or Twitter OAuth credentials")
        print("   See SOCIAL_MEDIA_API_SETUP.md for instructions")
        return False
    
    if bearer_token:
        print(f"✅ Bearer Token found: {bearer_token[:20]}...")
    elif api_key:
        print(f"✅ OAuth credentials found")
    
    # Initialize client
    try:
        client = TwitterAPIClient(twitter_config)
        print("✅ Twitter client initialized successfully")
    except Exception as e:
        print(f"❌ Error initializing Twitter client: {e}")
        return False
    
    # Test search
    try:
        keywords = twitter_config.get('keywords', ['python'])
        test_keyword = keywords[0] if keywords else 'python'
        
        print(f"\n🔍 Searching for tweets with keyword: '{test_keyword}'")
        tweets = client.search_tweets(test_keyword, max_results=5)
        
        if tweets:
            print(f"✅ Retrieved {len(tweets)} tweets")
            print("\n📝 Sample tweets:")
            for i, tweet in enumerate(tweets[:3], 1):
                author = tweet.get("author_username") or tweet.get("author_name") or "unknown"
                print(f"   {i}. {tweet['text'][:80]}...")
                print(f"      Author: {author}")
                print(f"      Time: {tweet['created_at']}")
                print()
            return True
        else:
            print("⚠️  No tweets found (might be sample data)")
            return False
            
    except Exception as e:
        print(f"❌ Error searching tweets: {e}")
        return False


def main():
    """Run Twitter API tests"""
    print("\n" + "🌐 SOCIAL MEDIA API CONNECTION TEST ".center(60, "="))
    print("\nThis script tests your Twitter API configuration.")
    print("Make sure you have:")
    print("  1. Added API credentials to .env file")
    print("  2. Enabled Twitter source in config/sources.yaml")
    print("  3. Configured keywords in sources.yaml")
    print("\nFor setup instructions, see: SOCIAL_MEDIA_API_SETUP.md")
    
    twitter_success = test_twitter()
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    
    if twitter_success:
        print("✅ Twitter API: Working")
    else:
        print("❌ Twitter API: Not configured or not working")
    
    print("\n" + "="*60)
    
    if twitter_success:
        print("\n🎉 SUCCESS! You can now run the ingestion service:")
        print("   python services/ingestion.py")
    else:
        print("\n⚠️  Twitter API not configured. Using sample data for testing.")
        print("   See SOCIAL_MEDIA_API_SETUP.md for API setup instructions.")
    
    print("\n")


if __name__ == "__main__":
    main()
