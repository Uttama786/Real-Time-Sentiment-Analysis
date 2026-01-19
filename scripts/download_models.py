"""
Download and setup NLP models
"""
import nltk
import spacy
import sys


def download_nltk_models():
    """Download required NLTK models"""
    print("Downloading NLTK models...")
    
    models = [
        'vader_lexicon',
        'punkt',
        'stopwords',
        'wordnet',
        'averaged_perceptron_tagger'
    ]
    
    for model in models:
        try:
            print(f"Downloading {model}...")
            nltk.download(model, quiet=True)
            print(f"✓ {model} downloaded successfully")
        except Exception as e:
            print(f"✗ Error downloading {model}: {e}")


def download_spacy_models():
    """Download spaCy models"""
    print("\nDownloading spaCy models...")
    
    try:
        # Check if model is already installed
        try:
            spacy.load("en_core_web_sm")
            print("✓ en_core_web_sm already installed")
        except OSError:
            print("Downloading en_core_web_sm...")
            import subprocess
            subprocess.check_call([
                sys.executable, "-m", "spacy", "download", "en_core_web_sm"
            ])
            print("✓ en_core_web_sm downloaded successfully")
    except Exception as e:
        print(f"✗ Error downloading spaCy model: {e}")


def verify_installations():
    """Verify all models are installed correctly"""
    print("\nVerifying installations...")
    
    try:
        # Test NLTK
        from nltk.sentiment import SentimentIntensityAnalyzer
        sia = SentimentIntensityAnalyzer()
        test_score = sia.polarity_scores("This is a test")
        print("✓ NLTK VADER working correctly")
    except Exception as e:
        print(f"✗ NLTK VADER error: {e}")
    
    try:
        # Test spaCy
        nlp = spacy.load("en_core_web_sm")
        doc = nlp("This is a test")
        print("✓ spaCy working correctly")
    except Exception as e:
        print(f"✗ spaCy error: {e}")
    
    try:
        # Test TextBlob
        from textblob import TextBlob
        blob = TextBlob("This is a test")
        sentiment = blob.sentiment
        print("✓ TextBlob working correctly")
    except Exception as e:
        print(f"✗ TextBlob error: {e}")


if __name__ == "__main__":
    print("=" * 60)
    print("NLP Models Setup Script")
    print("=" * 60)
    
    download_nltk_models()
    download_spacy_models()
    verify_installations()
    
    print("\n" + "=" * 60)
    print("Setup complete!")
    print("=" * 60)
