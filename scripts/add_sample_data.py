"""
Add sample sentiment data to database for testing real-time dashboard
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.sentiment_model import SentimentAnalyzer
from models.preprocessor import TextPreprocessor
from services.storage import StorageService
from datetime import datetime
import random

def add_sample_data():
    """Add sample sentiment data to database"""
    
    analyzer = SentimentAnalyzer()
    preprocessor = TextPreprocessor()
    storage = StorageService()
    
    # Sample texts with various sentiments
    sample_texts = [
        # Positive
        ("I absolutely love this product! It's amazing and exceeded all my expectations!", "twitter"),
        ("Best purchase I've ever made. Highly recommend to everyone!", "twitter"),
        ("Exceptional quality and fantastic customer service. Five stars!", "review"),
        ("This is incredible! So happy with my decision to buy this.", "twitter"),
        ("Outstanding performance. Worth every penny!", "review"),
        
        # Negative
        ("Terrible product. Complete waste of money and time.", "twitter"),
        ("Worst experience ever. Very disappointed with the quality.", "review"),
        ("Do not buy this! Poor quality and overpriced.", "twitter"),
        ("Horrible customer service. Will never buy from them again.", "review"),
        ("This is garbage. Broke after one day of use.", "twitter"),
        
        # Neutral
        ("It's okay. Nothing special but does the job.", "review"),
        ("Average product. Not bad, not great.", "twitter"),
        ("Decent quality for the price. Could be better.", "review"),
        ("It works as advertised. No complaints, no praises.", "twitter"),
        ("Standard product. Meets basic expectations.", "review"),
        
        # Mixed
        ("Good features but poor execution. Has potential.", "review"),
        ("Love the design but hate the functionality.", "twitter"),
        ("Great concept, disappointing results.", "review"),
        ("Nice packaging but product quality is questionable.", "twitter"),
        ("Excellent idea, mediocre implementation.", "review"),
        
        # News/Tech
        ("New AI breakthrough announced by researchers today.", "news"),
        ("Tech stock prices showing mixed results this quarter.", "news"),
        ("Innovation in renewable energy technology continues to advance.", "news"),
        ("Economic indicators suggest moderate growth ahead.", "news"),
        ("Latest smartphone release generates significant buzz.", "news"),
    ]
    
    print(f"\n{'='*60}")
    print("Adding Sample Sentiment Data to Database")
    print(f"{'='*60}\n")
    
    added_count = 0
    
    for text, source in sample_texts:
        try:
            # Preprocess
            processed_text = preprocessor.preprocess(text)
            
            if not processed_text:
                print(f"⚠️  Skipped (too short): {text[:50]}...")
                continue
            
            # Analyze
            result = analyzer.analyze(processed_text)
            
            # Store in database
            record = {
                'source': source,
                'text': text,
                'sentiment': result['sentiment'],
                'score': result['score'],
                'confidence': result['confidence'],
                'timestamp': datetime.utcnow().isoformat()
            }
            
            storage.save_sentiment(record)
            added_count += 1
            
            # Show progress
            sentiment_emoji = {
                'positive': '😊',
                'negative': '😞',
                'neutral': '😐'
            }.get(result['sentiment'], '❓')
            
            print(f"{sentiment_emoji} {result['sentiment'].upper():8} ({result['score']:+.3f}) - {text[:50]}...")
            
        except Exception as e:
            print(f"❌ Error processing: {text[:30]}... - {e}")
    
    print(f"\n{'-'*60}")
    print(f"✅ Added {added_count} sentiment records to database")
    print(f"{'-'*60}\n")
    
    # Show stats
    print("Fetching updated statistics...")
    from models.database import get_session, SentimentRecord
    session = get_session()
    
    total = session.query(SentimentRecord).count()
    positive = session.query(SentimentRecord).filter(SentimentRecord.sentiment == 'positive').count()
    negative = session.query(SentimentRecord).filter(SentimentRecord.sentiment == 'negative').count()
    neutral = session.query(SentimentRecord).filter(SentimentRecord.sentiment == 'neutral').count()
    
    session.close()
    
    print(f"\n📊 Database Statistics:")
    print(f"   Total Records: {total}")
    print(f"   Positive: {positive}")
    print(f"   Negative: {negative}")
    print(f"   Neutral: {neutral}")
    print(f"\n✅ Dashboard should now show real-time data!")
    print(f"   Refresh http://localhost:8050 to see the updates\n")


if __name__ == "__main__":
    add_sample_data()
