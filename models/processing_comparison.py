"""
Comparison framework for Batch vs Stream processing
Provides metrics and visualization data for performance comparison
"""
import time
import logging
from typing import List, Dict
from models.batch_processor import BatchProcessor
from models.stream_processor import StreamProcessor

logger = logging.getLogger(__name__)


class ProcessingComparison:
    """
    Framework for comparing batch and stream processing approaches
    """
    
    def __init__(self):
        """Initialize comparison framework"""
        self.batch_processor = BatchProcessor(batch_size=50, num_workers=4)
        self.stream_processor = StreamProcessor(window_size=100)
        
        self.comparison_results = {
            'batch': {},
            'stream': {},
            'comparison': {}
        }
        
        logger.info("Processing comparison framework initialized")
    
    def run_comparison(self, texts: List[str]) -> Dict:
        """
        Run both batch and stream processing on the same dataset
        
        Args:
            texts: List of texts to process
            
        Returns:
            Comprehensive comparison results
        """
        logger.info(f"Starting comparison with {len(texts)} texts")
        
        # Run batch processing
        print("\nRunning Batch Processing...")
        batch_start = time.time()
        batch_result = self.batch_processor.process_large_dataset(texts)
        batch_time = time.time() - batch_start
        
        # Run stream processing
        print("\nRunning Stream Processing...")
        stream_start = time.time()
        stream_results = []
        for text in texts:
            result = self.stream_processor.process_stream_item(text)
            stream_results.append(result)
        stream_time = time.time() - stream_start
        stream_stats = self.stream_processor.get_stats()
        
        # Calculate comparison metrics
        comparison = {
            'dataset_size': len(texts),
            'batch_total_time': round(batch_time, 2),
            'stream_total_time': round(stream_time, 2),
            'batch_throughput': round(len(texts) / batch_time, 2),
            'stream_throughput': round(len(texts) / stream_time, 2),
            'batch_avg_latency': round(batch_time / len(texts) * 1000, 2),
            'stream_avg_latency': stream_stats['average_latency_ms'],
            'time_difference': round(abs(batch_time - stream_time), 2),
            'faster_method': 'batch' if batch_time < stream_time else 'stream',
            'speed_improvement': round((max(batch_time, stream_time) / min(batch_time, stream_time) - 1) * 100, 2)
        }
        
        # Aggregate sentiment accuracy comparison
        batch_sentiments = [r.get('sentiment', 'neutral') for r in batch_result['results']]
        stream_sentiments = [r.get('sentiment', 'neutral') for r in stream_results]
        
        agreement = sum(1 for b, s in zip(batch_sentiments, stream_sentiments) if b == s)
        comparison['sentiment_agreement'] = round((agreement / len(texts)) * 100, 2)
        
        # Store results
        self.comparison_results = {
            'batch': batch_result,
            'stream': {
                'results': stream_results,
                'statistics': stream_stats
            },
            'comparison': comparison
        }
        
        logger.info(f"Comparison completed. Faster method: {comparison['faster_method']}")
        
        return self.comparison_results
    
    def get_flow_chart_data(self) -> Dict:
        """
        Generate data for flow chart visualization
        
        Returns:
            Dictionary with flow chart data for both approaches
        """
        return {
            'batch_flow': {
                'stages': [
                    {'name': 'Data Input', 'description': 'Large dataset loaded into memory', 'time_percent': 5},
                    {'name': 'Batch Division', 'description': 'Split data into fixed-size batches', 'time_percent': 5},
                    {'name': 'Preprocessing', 'description': 'Clean and normalize all texts in batch', 'time_percent': 20},
                    {'name': 'Parallel Processing', 'description': 'Analyze batches using thread pool', 'time_percent': 50},
                    {'name': 'Aggregation', 'description': 'Combine results and calculate statistics', 'time_percent': 15},
                    {'name': 'Output', 'description': 'Return complete dataset results', 'time_percent': 5}
                ],
                'characteristics': [
                    'High throughput',
                    'Optimized for large datasets',
                    'Parallel processing',
                    'Resource efficient',
                    'Delayed results'
                ]
            },
            'stream_flow': {
                'stages': [
                    {'name': 'Data Arrival', 'description': 'Individual item received', 'time_percent': 5},
                    {'name': 'Immediate Processing', 'description': 'Process item as it arrives', 'time_percent': 15},
                    {'name': 'Preprocessing', 'description': 'Clean and normalize single text', 'time_percent': 20},
                    {'name': 'Analysis', 'description': 'Perform sentiment analysis', 'time_percent': 40},
                    {'name': 'Metrics Update', 'description': 'Update sliding window statistics', 'time_percent': 10},
                    {'name': 'Output', 'description': 'Return result immediately', 'time_percent': 10}
                ],
                'characteristics': [
                    'Low latency',
                    'Real-time results',
                    'Sequential processing',
                    'Continuous operation',
                    'Immediate feedback'
                ]
            },
            'comparison_table': [
                {'metric': 'Latency', 'batch': 'High (seconds)', 'stream': 'Low (milliseconds)'},
                {'metric': 'Throughput', 'batch': 'Very High', 'stream': 'Moderate'},
                {'metric': 'Resource Usage', 'batch': 'Burst (peaks)', 'stream': 'Steady (constant)'},
                {'metric': 'Use Case', 'batch': 'Historical Analysis', 'stream': 'Real-time Monitoring'},
                {'metric': 'Scalability', 'batch': 'Horizontal (workers)', 'stream': 'Vertical (single item)'},
                {'metric': 'Result Delivery', 'batch': 'All at once', 'stream': 'Item by item'},
                {'metric': 'Memory Footprint', 'batch': 'Large (full dataset)', 'stream': 'Small (sliding window)'}
            ]
        }
    
    def get_performance_metrics(self) -> Dict:
        """
        Get detailed performance metrics for visualization
        
        Returns:
            Dictionary with performance metrics
        """
        if not self.comparison_results.get('comparison'):
            return {}
        
        comp = self.comparison_results['comparison']
        
        return {
            'throughput_comparison': {
                'batch': comp.get('batch_throughput', 0),
                'stream': comp.get('stream_throughput', 0)
            },
            'latency_comparison': {
                'batch': comp.get('batch_avg_latency', 0),
                'stream': comp.get('stream_avg_latency', 0)
            },
            'total_time_comparison': {
                'batch': comp.get('batch_total_time', 0),
                'stream': comp.get('stream_total_time', 0)
            },
            'winner': comp.get('faster_method', 'unknown'),
            'improvement': comp.get('speed_improvement', 0)
        }


if __name__ == "__main__":
    # Test comparison
    comparison = ProcessingComparison()
    
    test_texts = [
        "I love this product!",
        "This is terrible.",
        "It's okay, nothing special.",
        "Amazing experience!",
        "Worst purchase ever.",
    ] * 10  # 50 texts
    
    results = comparison.run_comparison(test_texts)
    
    print("\n" + "="*60)
    print("COMPARISON RESULTS")
    print("="*60)
    
    comp = results['comparison']
    print(f"\nDataset Size: {comp['dataset_size']} texts")
    print(f"\nBatch Processing:")
    print(f"  Total Time: {comp['batch_total_time']}s")
    print(f"  Throughput: {comp['batch_throughput']} items/s")
    print(f"  Avg Latency: {comp['batch_avg_latency']}ms")
    
    print(f"\nStream Processing:")
    print(f"  Total Time: {comp['stream_total_time']}s")
    print(f"  Throughput: {comp['stream_throughput']} items/s")
    print(f"  Avg Latency: {comp['stream_avg_latency']}ms")
    
    print(f"\nComparison:")
    print(f"  Faster Method: {comp['faster_method'].upper()}")
    print(f"  Speed Improvement: {comp['speed_improvement']}%")
    print(f"  Sentiment Agreement: {comp['sentiment_agreement']}%")
    
    # Get flow chart data
    flow_data = comparison.get_flow_chart_data()
    print(f"\nBatch Characteristics: {', '.join(flow_data['batch_flow']['characteristics'])}")
    print(f"Stream Characteristics: {', '.join(flow_data['stream_flow']['characteristics'])}")
