"""
Text preprocessing utilities for sentiment analysis
"""
import re
import yaml
from typing import List


class TextPreprocessor:
    """Preprocess text data for sentiment analysis"""
    
    def __init__(self, config_path='config/models.yaml'):
        """Initialize preprocessor with configuration"""
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        self.config = config['preprocessing']
    
    def remove_urls(self, text: str) -> str:
        """Remove URLs from text"""
        return re.sub(r'http\S+|www.\S+', '', text)
    
    def remove_mentions(self, text: str) -> str:
        """Remove @mentions from text"""
        return re.sub(r'@\w+', '', text)
    
    def remove_hashtags(self, text: str) -> str:
        """Remove hashtags from text"""
        return re.sub(r'#\w+', '', text)
    
    def remove_punctuation(self, text: str) -> str:
        """Remove punctuation from text"""
        return re.sub(r'[^\w\s]', '', text)
    
    def remove_extra_whitespace(self, text: str) -> str:
        """Remove extra whitespace"""
        return ' '.join(text.split())
    
    def preprocess(self, text: str) -> str:
        """
        Apply preprocessing pipeline to text
        
        Args:
            text: Input text to preprocess
            
        Returns:
            Preprocessed text
        """
        if not text or not isinstance(text, str):
            return ""
        
        # Apply preprocessing steps based on config
        if self.config['lowercase']:
            text = text.lower()
        
        if self.config['remove_urls']:
            text = self.remove_urls(text)
        
        if self.config['remove_mentions']:
            text = self.remove_mentions(text)
        
        if self.config['remove_hashtags']:
            text = self.remove_hashtags(text)
        
        if self.config['remove_punctuation']:
            text = self.remove_punctuation(text)
        
        # Always remove extra whitespace
        text = self.remove_extra_whitespace(text)
        
        # Check length constraints
        if len(text) < self.config['min_length']:
            return ""
        
        if len(text) > self.config['max_length']:
            text = text[:self.config['max_length']]
        
        return text
    
    def batch_preprocess(self, texts: List[str]) -> List[str]:
        """Preprocess multiple texts"""
        return [self.preprocess(text) for text in texts]
    
    def is_valid_text(self, text: str) -> bool:
        """Check if text is valid after preprocessing"""
        preprocessed = self.preprocess(text)
        return len(preprocessed) >= self.config['min_length']


if __name__ == "__main__":
    # Test the preprocessor
    preprocessor = TextPreprocessor()
    
    test_texts = [
        "Check out this amazing article! https://example.com @user #AI #MachineLearning",
        "THIS IS IN ALL CAPS WITH EXTRA     SPACES!!!",
        "Short",
        "@mention1 @mention2 Just some mentions and #hashtags #test",
    ]
    
    for text in test_texts:
        processed = preprocessor.preprocess(text)
        print(f"\nOriginal: {text}")
        print(f"Processed: {processed}")
        print(f"Valid: {preprocessor.is_valid_text(text)}")
