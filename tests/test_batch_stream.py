"""
Test script for Batch and Stream Processing features
Run this to verify the new features are working correctly
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.batch_processor import BatchProcessor
from models.stream_processor import StreamProcessor
from models.processing_comparison import ProcessingComparison

def test_batch_processing():
    """Test batch processing functionality"""
    print("\n" + "="*60)
    print("TESTING BATCH PROCESSING")
    print("="*60)
    
    processor = BatchProcessor(batch_size=10, num_workers=2)
    
    test_texts = [
        "I absolutely love this product!",
        "This is terrible and disappointing.",
        "It's okay, nothing special.",
        "Best experience ever!",
        "Worst service I've had.",
    ] * 10  # 50 texts
    
    result = processor.process_large_dataset(test_texts)
    
    print(f"\n✓ Processed {result['statistics']['total_items']} texts")
    print(f"✓ Total Time: {result['statistics']['total_time']}s")
    print(f"✓ Throughput: {result['statistics']['throughput']} items/s")
    print(f"✓ Avg Time per Item: {result['statistics']['avg_time_per_item']}s")
    print(f"✓ Sentiment Distribution: {result['statistics']['sentiment_distribution']}")
    
    return True


def test_stream_processing():
    """Test stream processing functionality"""
    print("\n" + "="*60)
    print("TESTING STREAM PROCESSING")
    print("="*60)
    
    processor = StreamProcessor(window_size=10)
    
    test_texts = [
        "I love this product!",
        "This is terrible.",
        "It's okay, nothing special.",
        "Amazing experience!",
        "Worst purchase ever.",
    ]
    
    print("\nProcessing stream items...")
    for i, text in enumerate(test_texts):
        result = processor.process_stream_item(text)
        print(f"\n  Item {i+1}: {text[:40]}...")
        print(f"    → Sentiment: {result['sentiment']}")
        print(f"    → Score: {result['score']}")
        print(f"    → Latency: {result['latency_ms']}ms")
    
    stats = processor.get_stats()
    window_stats = processor.get_window_statistics()
    
    print(f"\n✓ Total Processed: {stats['total_processed']}")
    print(f"✓ Average Latency: {stats['average_latency_ms']}ms")
    print(f"✓ Overall Throughput: {stats['overall_throughput']} items/s")
    print(f"✓ Window Sentiment Distribution: {window_stats['sentiment_distribution']}")
    
    return True


def test_comparison():
    """Test comparison framework"""
    print("\n" + "="*60)
    print("TESTING COMPARISON FRAMEWORK")
    print("="*60)
    
    comparison = ProcessingComparison()
    
    test_texts = [
        "I love this product!",
        "This is terrible.",
        "It's okay, nothing special.",
        "Amazing experience!",
        "Worst purchase ever.",
    ] * 10  # 50 texts
    
    print(f"\nRunning comparison with {len(test_texts)} texts...")
    results = comparison.run_comparison(test_texts)
    
    comp = results['comparison']
    
    print("\n" + "-"*60)
    print("COMPARISON RESULTS")
    print("-"*60)
    
    print(f"\n📊 Dataset Size: {comp['dataset_size']} texts")
    
    print(f"\n⚡ Batch Processing:")
    print(f"   Time: {comp['batch_total_time']}s")
    print(f"   Throughput: {comp['batch_throughput']} items/s")
    print(f"   Avg Latency: {comp['batch_avg_latency']}ms")
    
    print(f"\n🌊 Stream Processing:")
    print(f"   Time: {comp['stream_total_time']}s")
    print(f"   Throughput: {comp['stream_throughput']} items/s")
    print(f"   Avg Latency: {comp['stream_avg_latency']}ms")
    
    print(f"\n🏆 Winner: {comp['faster_method'].upper()}")
    print(f"📈 Speed Improvement: {comp['speed_improvement']}%")
    print(f"🎯 Sentiment Agreement: {comp['sentiment_agreement']}%")
    
    # Test flow chart data
    flow_data = comparison.get_flow_chart_data()
    print(f"\n✓ Flow chart data generated")
    print(f"  - Batch stages: {len(flow_data['batch_flow']['stages'])}")
    print(f"  - Stream stages: {len(flow_data['stream_flow']['stages'])}")
    print(f"  - Comparison metrics: {len(flow_data['comparison_table'])}")
    
    return True


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("BATCH VS STREAM PROCESSING - FEATURE TEST")
    print("="*60)
    
    all_passed = True
    
    try:
        # Test batch processing
        if test_batch_processing():
            print("\n✅ Batch Processing: PASSED")
        else:
            print("\n❌ Batch Processing: FAILED")
            all_passed = False
    except Exception as e:
        print(f"\n❌ Batch Processing: FAILED - {e}")
        all_passed = False
    
    try:
        # Test stream processing
        if test_stream_processing():
            print("\n✅ Stream Processing: PASSED")
        else:
            print("\n❌ Stream Processing: FAILED")
            all_passed = False
    except Exception as e:
        print(f"\n❌ Stream Processing: FAILED - {e}")
        all_passed = False
    
    try:
        # Test comparison
        if test_comparison():
            print("\n✅ Comparison Framework: PASSED")
        else:
            print("\n❌ Comparison Framework: FAILED")
            all_passed = False
    except Exception as e:
        print(f"\n❌ Comparison Framework: FAILED - {e}")
        all_passed = False
    
    print("\n" + "="*60)
    if all_passed:
        print("🎉 ALL TESTS PASSED!")
    else:
        print("⚠️  SOME TESTS FAILED")
    print("="*60 + "\n")
    
    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
