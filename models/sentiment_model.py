"""
Sentiment analysis model wrapper
"""
import yaml
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from typing import Dict, Tuple


class SentimentAnalyzer:
    """Main sentiment analyzer that uses multiple models"""
    
    def __init__(self, config_path='config/models.yaml'):
        """Initialize sentiment analyzer with configuration"""
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.vader = SentimentIntensityAnalyzer()
        self.models_config = self.config['sentiment_models']
        self.thresholds = self.config['thresholds']
        
    def analyze_vader(self, text: str) -> Dict[str, float]:
        """Analyze sentiment using VADER"""
        scores = self.vader.polarity_scores(text)
        return scores
    
    def analyze_textblob(self, text: str) -> Tuple[float, float]:
        """Analyze sentiment using TextBlob"""
        blob = TextBlob(text)
        return blob.sentiment.polarity, blob.sentiment.subjectivity
    
    def analyze(self, text: str) -> Dict[str, any]:
        """
        Perform comprehensive sentiment analysis
        
        Returns:
            dict: {
                'sentiment': 'positive'|'negative'|'neutral',
                'score': float (-1 to 1),
                'confidence': float (0 to 1),
                'details': dict with individual model scores
            }
        """
        results = {'details': {}}
        
        # VADER analysis (primary)
        if self.models_config['primary']['enabled']:
            vader_scores = self.analyze_vader(text)
            results['details']['vader'] = vader_scores
            compound_score = vader_scores['compound']
        else:
            compound_score = 0
        
        # TextBlob analysis (secondary)
        if self.models_config['secondary']['enabled']:
            polarity, subjectivity = self.analyze_textblob(text)
            results['details']['textblob'] = {
                'polarity': polarity,
                'subjectivity': subjectivity
            }
            # Average with VADER if both enabled
            final_score = (compound_score + polarity) / 2
        else:
            final_score = compound_score
        
        # Determine sentiment label
        pos_threshold = self.thresholds['positive']
        neg_threshold = self.thresholds['negative']
        
        if final_score >= pos_threshold:
            sentiment = 'positive'
        elif final_score <= neg_threshold:
            sentiment = 'negative'
        else:
            sentiment = 'neutral'
        
        # Calculate confidence (using absolute value of score)
        confidence = min(abs(final_score), 1.0)
        
        results.update({
            'sentiment': sentiment,
            'score': round(final_score, 4),
            'confidence': round(confidence, 4)
        })
        
        return results
    
    def batch_analyze(self, texts: list) -> list:
        """Analyze multiple texts"""
        return [self.analyze(text) for text in texts]


if __name__ == "__main__":
    # Test the analyzer
    analyzer = SentimentAnalyzer()
    
    test_texts = [
        "I absolutely love this product! It's amazing!",
        "This is terrible and disappointing.",
        "It's okay, nothing special.",
        "Best experience ever! Highly recommended!",
        "Worst service I've ever had."
    ]
    
    for text in test_texts:
        result = analyzer.analyze(text)
        print(f"\nText: {text}")
        print(f"Sentiment: {result['sentiment']}")
        print(f"Score: {result['score']}")
        print(f"Confidence: {result['confidence']}")
