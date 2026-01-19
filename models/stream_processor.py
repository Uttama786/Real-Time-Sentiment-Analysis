"""
Stream Processing Model for Real-time Sentiment Analysis
Processes data streams with low latency and real-time metrics
"""
import time
import logging
from typing import Dict, Optional
from collections import deque
from datetime import datetime
from models.sentiment_model import SentimentAnalyzer
from models.preprocessor import TextPreprocessor

logger = logging.getLogger(__name__)


class StreamProcessor:
    """
    Stream processing model for real-time sentiment analysis
    Optimized for low latency and continuous data streams
    """
    
    def __init__(self, window_size: int = 100):
        """
        Initialize stream processor
        
        Args:
            window_size: Size of sliding window for metrics calculation
        """
        self.window_size = window_size
        self.analyzer = SentimentAnalyzer()
        self.preprocessor = TextPreprocessor()
        
        # Sliding window for recent results
        self.recent_results = deque(maxlen=window_size)
        self.recent_latencies = deque(maxlen=window_size)
        
        self.stats = {
            'total_processed': 0,
            'total_time': 0,
            'avg_latency': 0,
            'min_latency': float('inf'),
            'max_latency': 0,
            'current_throughput': 0
        }
        
        self.start_time = time.time()
        
        logger.info(f"Stream processor initialized with window_size={window_size}")
    
    def process_stream_item(self, text: str, metadata: Optional[Dict] = None) -> Dict:
        """
        Process a single item from the stream
        
        Args:
            text: Text string to analyze
            metadata: Optional metadata about the item
            
        Returns:
            Analysis result with latency metrics
        """
        start_time = time.time()
        
        # Preprocess text
        processed_text = self.preprocessor.preprocess(text)
        
        if not processed_text:
            return {
                'original_text': text,
                'sentiment': 'neutral',
                'score': 0.0,
                'error': 'Text too short after preprocessing'
            }
        
        # Analyze sentiment
        result = self.analyzer.analyze(processed_text)
        result['original_text'] = text
        result['timestamp'] = datetime.utcnow().isoformat()
        
        if metadata:
            result['metadata'] = metadata
        
        # Calculate latency
        latency = time.time() - start_time
        result['latency_ms'] = round(latency * 1000, 2)
        
        # Update statistics
        self.stats['total_processed'] += 1
        self.stats['total_time'] += latency
        self.stats['avg_latency'] = self.stats['total_time'] / self.stats['total_processed']
        self.stats['min_latency'] = min(self.stats['min_latency'], latency)
        self.stats['max_latency'] = max(self.stats['max_latency'], latency)
        
        # Update sliding window
        self.recent_results.append(result)
        self.recent_latencies.append(latency)
        
        # Calculate current throughput (items/second in window)
        if len(self.recent_latencies) > 1:
            window_time = sum(self.recent_latencies)
            self.stats['current_throughput'] = len(self.recent_latencies) / window_time if window_time > 0 else 0
        
        logger.debug(f"Processed stream item in {latency*1000:.2f}ms")
        
        return result
    
    def get_window_statistics(self) -> Dict:
        """
        Get statistics for the current sliding window
        
        Returns:
            Dictionary with window statistics
        """
        if not self.recent_results:
            return {
                'window_size': 0,
                'sentiment_distribution': {},
                'average_score': 0,
                'average_latency': 0
            }
        
        sentiment_counts = {'positive': 0, 'negative': 0, 'neutral': 0}
        total_score = 0
        
        for result in self.recent_results:
            sentiment = result.get('sentiment', 'neutral')
            if sentiment in sentiment_counts:
                sentiment_counts[sentiment] += 1
            total_score += result.get('score', 0)
        
        return {
            'window_size': len(self.recent_results),
            'sentiment_distribution': sentiment_counts,
            'average_score': round(total_score / len(self.recent_results), 4),
            'average_latency_ms': round(sum(self.recent_latencies) / len(self.recent_latencies) * 1000, 2),
            'min_latency_ms': round(min(self.recent_latencies) * 1000, 2) if self.recent_latencies else 0,
            'max_latency_ms': round(max(self.recent_latencies) * 1000, 2) if self.recent_latencies else 0
        }
    
    def get_stats(self) -> Dict:
        """
        Get overall processing statistics
        
        Returns:
            Dictionary with overall statistics
        """
        uptime = time.time() - self.start_time
        
        return {
            'total_processed': self.stats['total_processed'],
            'uptime_seconds': round(uptime, 2),
            'average_latency_ms': round(self.stats['avg_latency'] * 1000, 2),
            'min_latency_ms': round(self.stats['min_latency'] * 1000, 2) if self.stats['min_latency'] != float('inf') else 0,
            'max_latency_ms': round(self.stats['max_latency'] * 1000, 2),
            'overall_throughput': round(self.stats['total_processed'] / uptime, 2) if uptime > 0 else 0,
            'current_throughput': round(self.stats['current_throughput'], 2),
            'processing_mode': 'stream'
        }
    
    def reset_stats(self):
        """Reset all statistics"""
        self.stats = {
            'total_processed': 0,
            'total_time': 0,
            'avg_latency': 0,
            'min_latency': float('inf'),
            'max_latency': 0,
            'current_throughput': 0
        }
        self.recent_results.clear()
        self.recent_latencies.clear()
        self.start_time = time.time()
        logger.info("Statistics reset")


if __name__ == "__main__":
    # Test stream processor
    processor = StreamProcessor(window_size=10)
    
    test_texts = [
        "I love this product!",
        "This is terrible.",
        "It's okay, nothing special.",
        "Amazing experience!",
        "Worst purchase ever.",
        "Great service and quality!",
        "Not worth the money.",
        "Exceeded my expectations!",
        "Poor quality control.",
        "Highly recommend this!"
    ]
    
    print("\nStream Processing Test:")
    print("-" * 60)
    
    for i, text in enumerate(test_texts):
        result = processor.process_stream_item(text)
        print(f"\nItem {i+1}:")
        print(f"  Text: {text}")
        print(f"  Sentiment: {result['sentiment']}")
        print(f"  Score: {result['score']}")
        print(f"  Latency: {result['latency_ms']}ms")
    
    print("\n" + "="*60)
    print("Stream Statistics:")
    stats = processor.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    print("\nWindow Statistics:")
    window_stats = processor.get_window_statistics()
    for key, value in window_stats.items():
        print(f"  {key}: {value}")
