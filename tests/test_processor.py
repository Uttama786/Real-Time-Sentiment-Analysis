"""
Tests for sentiment processing
"""
import pytest
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.sentiment_model import SentimentAnalyzer
from models.preprocessor import TextPreprocessor


class TestSentimentAnalyzer:
    """Test cases for sentiment analysis"""
    
    @pytest.fixture
    def analyzer(self):
        """Create analyzer instance"""
        return SentimentAnalyzer()
    
    def test_analyzer_initialization(self, analyzer):
        """Test analyzer initializes correctly"""
        assert analyzer is not None
        assert analyzer.vader is not None
    
    def test_positive_sentiment(self, analyzer):
        """Test positive sentiment detection"""
        text = "I absolutely love this! It's amazing and wonderful!"
        result = analyzer.analyze(text)
        
        assert result['sentiment'] == 'positive'
        assert result['score'] > 0
        assert 0 <= result['confidence'] <= 1
    
    def test_negative_sentiment(self, analyzer):
        """Test negative sentiment detection"""
        text = "This is terrible and awful. I hate it!"
        result = analyzer.analyze(text)
        
        assert result['sentiment'] == 'negative'
        assert result['score'] < 0
        assert 0 <= result['confidence'] <= 1
    
    def test_neutral_sentiment(self, analyzer):
        """Test neutral sentiment detection"""
        text = "This is a table."
        result = analyzer.analyze(text)
        
        assert result['sentiment'] in ['neutral', 'positive', 'negative']
        assert -1 <= result['score'] <= 1
        assert 0 <= result['confidence'] <= 1
    
    def test_batch_analysis(self, analyzer):
        """Test batch sentiment analysis"""
        texts = [
            "Great product!",
            "Poor quality.",
            "It's okay."
        ]
        
        results = analyzer.batch_analyze(texts)
        assert len(results) == 3
        assert all('sentiment' in r for r in results)


class TestTextPreprocessor:
    """Test cases for text preprocessing"""
    
    @pytest.fixture
    def preprocessor(self):
        """Create preprocessor instance"""
        return TextPreprocessor()
    
    def test_url_removal(self, preprocessor):
        """Test URL removal"""
        text = "Check this out https://example.com"
        result = preprocessor.remove_urls(text)
        assert "https://" not in result
    
    def test_mention_removal(self, preprocessor):
        """Test mention removal"""
        text = "@user1 @user2 hello"
        result = preprocessor.remove_mentions(text)
        assert "@user" not in result
    
    def test_lowercase(self, preprocessor):
        """Test lowercase conversion"""
        text = "HELLO WORLD"
        result = preprocessor.preprocess(text)
        assert result.islower()
    
    def test_whitespace_removal(self, preprocessor):
        """Test extra whitespace removal"""
        text = "hello    world"
        result = preprocessor.remove_extra_whitespace(text)
        assert "    " not in result
    
    def test_valid_text(self, preprocessor):
        """Test valid text check"""
        valid_text = "This is a valid text"
        invalid_text = "ab"
        
        assert preprocessor.is_valid_text(valid_text)
        assert not preprocessor.is_valid_text(invalid_text)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
