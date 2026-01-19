"""
Batch Processing Model for Sentiment Analysis
Processes large datasets in batches with performance metrics
"""
import time
import logging
from typing import List, Dict
from concurrent.futures import ThreadPoolExecutor, as_completed
from models.sentiment_model import SentimentAnalyzer
from models.preprocessor import TextPreprocessor

logger = logging.getLogger(__name__)


class BatchProcessor:
    """
    Batch processing model for analyzing large datasets
    Optimized for throughput and resource efficiency
    """
    
    def __init__(self, batch_size: int = 100, num_workers: int = 4):
        """
        Initialize batch processor
        
        Args:
            batch_size: Number of items to process in each batch
            num_workers: Number of parallel workers for processing
        """
        self.batch_size = batch_size
        self.num_workers = num_workers
        self.analyzer = SentimentAnalyzer()
        self.preprocessor = TextPreprocessor()
        
        self.stats = {
            'total_processed': 0,
            'total_time': 0,
            'avg_time_per_item': 0,
            'throughput': 0
        }
        
        logger.info(f"Batch processor initialized with batch_size={batch_size}, workers={num_workers}")
    
    def process_batch(self, texts: List[str]) -> List[Dict]:
        """
        Process a batch of texts
        
        Args:
            texts: List of text strings to analyze
            
        Returns:
            List of analysis results
        """
        start_time = time.time()
        results = []
        
        # Preprocess all texts
        processed_texts = [self.preprocessor.preprocess(text) for text in texts]
        
        # Analyze in parallel using thread pool
        with ThreadPoolExecutor(max_workers=self.num_workers) as executor:
            future_to_text = {
                executor.submit(self.analyzer.analyze, text): (i, text) 
                for i, text in enumerate(processed_texts) if text
            }
            
            for future in as_completed(future_to_text):
                idx, original_text = future_to_text[future]
                try:
                    result = future.result()
                    result['original_text'] = texts[idx]
                    results.append(result)
                except Exception as e:
                    logger.error(f"Error processing text at index {idx}: {e}")
                    results.append({
                        'original_text': texts[idx],
                        'sentiment': 'error',
                        'score': 0.0,
                        'error': str(e)
                    })
        
        # Update statistics
        elapsed_time = time.time() - start_time
        self.stats['total_processed'] += len(texts)
        self.stats['total_time'] += elapsed_time
        self.stats['avg_time_per_item'] = self.stats['total_time'] / self.stats['total_processed']
        self.stats['throughput'] = self.stats['total_processed'] / self.stats['total_time']
        
        logger.info(f"Processed batch of {len(texts)} items in {elapsed_time:.2f}s")
        
        return results
    
    def process_large_dataset(self, texts: List[str]) -> Dict:
        """
        Process a large dataset by splitting into batches
        
        Args:
            texts: Large list of text strings
            
        Returns:
            Dictionary with results and statistics
        """
        start_time = time.time()
        all_results = []
        
        # Split into batches
        num_batches = (len(texts) + self.batch_size - 1) // self.batch_size
        logger.info(f"Processing {len(texts)} texts in {num_batches} batches")
        
        for i in range(0, len(texts), self.batch_size):
            batch = texts[i:i + self.batch_size]
            batch_results = self.process_batch(batch)
            all_results.extend(batch_results)
            
            logger.info(f"Completed batch {i//self.batch_size + 1}/{num_batches}")
        
        total_time = time.time() - start_time
        
        # Aggregate statistics
        sentiment_counts = {'positive': 0, 'negative': 0, 'neutral': 0}
        total_score = 0
        
        for result in all_results:
            sentiment = result.get('sentiment', 'neutral')
            if sentiment in sentiment_counts:
                sentiment_counts[sentiment] += 1
            total_score += result.get('score', 0)
        
        return {
            'results': all_results,
            'statistics': {
                'total_items': len(texts),
                'total_time': round(total_time, 2),
                'avg_time_per_item': round(total_time / len(texts), 4),
                'throughput': round(len(texts) / total_time, 2),
                'sentiment_distribution': sentiment_counts,
                'average_score': round(total_score / len(texts), 4) if all_results else 0
            },
            'processing_mode': 'batch'
        }
    
    def get_stats(self) -> Dict:
        """Get current processing statistics"""
        return self.stats.copy()


if __name__ == "__main__":
    # Test batch processor
    processor = BatchProcessor(batch_size=10, num_workers=2)
    
    test_texts = [
        "I love this product!",
        "This is terrible.",
        "It's okay, nothing special.",
        "Amazing experience!",
        "Worst purchase ever.",
    ] * 20  # 100 texts
    
    result = processor.process_large_dataset(test_texts)
    print(f"\nBatch Processing Results:")
    print(f"Total items: {result['statistics']['total_items']}")
    print(f"Total time: {result['statistics']['total_time']}s")
    print(f"Throughput: {result['statistics']['throughput']} items/s")
    print(f"Sentiment distribution: {result['statistics']['sentiment_distribution']}")
