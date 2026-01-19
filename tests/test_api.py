"""
Tests for API endpoints
"""
import pytest
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from app import app

client = TestClient(app)


class TestAPI:
    """Test cases for API endpoints"""
    
    def test_root_endpoint(self):
        """Test root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        assert "message" in response.json()
    
    def test_health_check(self):
        """Test health check endpoint"""
        response = client.get("/api/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
    
    def test_analyze_endpoint(self):
        """Test sentiment analysis endpoint"""
        response = client.post(
            "/api/analyze",
            json={"text": "This is an amazing product!"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "sentiment" in data
        assert "score" in data
        assert "confidence" in data
    
    def test_analyze_empty_text(self):
        """Test analysis with empty text"""
        response = client.post(
            "/api/analyze",
            json={"text": ""}
        )
        assert response.status_code == 400
    
    def test_sentiments_endpoint(self):
        """Test get sentiments endpoint"""
        response = client.get("/api/sentiments?limit=10")
        assert response.status_code == 200
        data = response.json()
        assert "count" in data
        assert "records" in data
    
    def test_stats_endpoint(self):
        """Test statistics endpoint"""
        response = client.get("/api/stats?timerange=24h")
        assert response.status_code == 200
        data = response.json()
        assert "total_records" in data
    
    def test_stats_invalid_timerange(self):
        """Test stats with invalid timerange"""
        response = client.get("/api/stats?timerange=invalid")
        assert response.status_code == 400


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
