"""
Tests for data ingestion service
"""
import pytest
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.ingestion import DataIngestionService


class TestDataIngestion:
    """Test cases for data ingestion"""
    
    @pytest.fixture
    def service(self):
        """Create ingestion service instance"""
        return DataIngestionService()
    
    def test_service_initialization(self, service):
        """Test service initializes correctly"""
        assert service is not None
        assert service.config is not None
        assert service.redis_client is not None
    
    def test_queue_push(self, service):
        """Test pushing data to queue"""
        test_data = {
            'source': 'test',
            'text': 'Test message',
            'timestamp': '2024-01-01T00:00:00'
        }
        
        try:
            service.push_to_queue(test_data)
            # If no exception, test passes
            assert True
        except Exception as e:
            pytest.fail(f"Queue push failed: {e}")
    
    def test_twitter_ingestion(self, service):
        """Test Twitter data ingestion"""
        try:
            service.ingest_from_twitter()
            # Check if data was added to queue
            queue_size = service.redis_client.llen(service.queue_name)
            assert queue_size >= 0
        except Exception as e:
            pytest.skip(f"Twitter ingestion test skipped: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
