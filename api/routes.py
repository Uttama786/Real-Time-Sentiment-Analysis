"""
FastAPI routes for sentiment analysis API
"""
import os
import sys
from datetime import datetime, timedelta
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.sentiment_model import SentimentAnalyzer
from models.preprocessor import TextPreprocessor
from models.batch_processor import BatchProcessor
from models.stream_processor import StreamProcessor
from models.processing_comparison import ProcessingComparison
from services.storage import StorageService

router = APIRouter()

# Initialize services
analyzer = SentimentAnalyzer()
preprocessor = TextPreprocessor()
storage = StorageService()
batch_processor = BatchProcessor(batch_size=50, num_workers=4)
stream_processor = StreamProcessor(window_size=100)
comparison_framework = ProcessingComparison()


# Request/Response models
class AnalyzeRequest(BaseModel):
    text: str
    source: Optional[str] = "api"


class AnalyzeResponse(BaseModel):
    sentiment: str
    score: float
    confidence: float
    details: dict


class SentimentRecord(BaseModel):
    id: int
    source: str
    text: str
    sentiment: str
    score: float
    confidence: float
    timestamp: str
    metadata: Optional[str] = None


class BatchAnalyzeRequest(BaseModel):
    texts: List[str]


class BatchAnalyzeResponse(BaseModel):
    results: List[dict]
    statistics: dict
    processing_mode: str


class StreamAnalyzeRequest(BaseModel):
    text: str
    metadata: Optional[dict] = None


class StreamAnalyzeResponse(BaseModel):
    sentiment: str
    score: float
    confidence: float
    latency_ms: float
    timestamp: str
    details: dict


@router.get("/")
async def root():
    """API root endpoint"""
    return {
        "message": "Sentiment Analysis API",
        "version": "1.0.0",
        "endpoints": {
            "analyze": "/api/analyze",
            "batch_analyze": "/api/batch-analyze",
            "stream_analyze": "/api/stream-analyze",
            "compare_processing": "/api/compare-processing",
            "sentiments": "/api/sentiments",
            "stats": "/api/stats",
            "batch_stats": "/api/batch-stats",
            "stream_stats": "/api/stream-stats",
            "history": "/api/history",
            "health": "/api/health"
        }
    }


@router.post("/api/analyze", response_model=AnalyzeResponse)
async def analyze_text(request: AnalyzeRequest):
    """
    Analyze sentiment of custom text
    
    Example:
    ```
    POST /api/analyze
    {
        "text": "This is amazing!",
        "source": "user_input"
    }
    ```
    """
    try:
        # Preprocess text
        processed_text = preprocessor.preprocess(request.text)
        
        if not processed_text:
            raise HTTPException(
                status_code=400,
                detail="Text is too short or invalid after preprocessing"
            )
        
        # Analyze sentiment
        result = analyzer.analyze(processed_text)
        
        # Save to database in real-time
        try:
            record = {
                'source': 'api',
                'text': request.text,
                'sentiment': result['sentiment'],
                'score': result['score'],
                'confidence': result['confidence'],
                'timestamp': datetime.utcnow().isoformat(),
                'metadata': '{}'
            }
            storage.save_sentiment(record)
        except Exception as db_error:
            print(f"Warning: Could not save to database: {db_error}")
            # Continue anyway - don't fail the API response
        
        return AnalyzeResponse(**result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/sentiments")
async def get_sentiments(limit: int = Query(default=100, le=1000)):
    """
    Get recent sentiment records
    
    Query Parameters:
    - limit: Maximum number of records to return (default: 100, max: 1000)
    """
    try:
        records = storage.get_recent_sentiments(limit=limit)
        return {
            "count": len(records),
            "records": records
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/stats")
async def get_statistics(timerange: str = Query(default="24h")):
    """
    Get sentiment statistics
    
    Query Parameters:
    - timerange: Time range for statistics (e.g., '1h', '24h', '7d', '30d')
    """
    try:
        # Parse timerange
        timerange_map = {
            '1h': 1,
            '6h': 6,
            '12h': 12,
            '24h': 24,
            '7d': 24 * 7,
            '30d': 24 * 30
        }
        
        hours = timerange_map.get(timerange)
        if hours is None:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid timerange. Use one of: {list(timerange_map.keys())}"
            )
        
        stats = storage.get_sentiment_stats(hours=hours)
        return stats
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/history")
async def get_history(
    start: str = Query(..., description="Start date (ISO format)"),
    end: str = Query(..., description="End date (ISO format)")
):
    """
    Get historical sentiment data
    
    Query Parameters:
    - start: Start date in ISO format (e.g., '2024-01-01')
    - end: End date in ISO format (e.g., '2024-01-31')
    """
    try:
        # Parse dates
        start_date = datetime.fromisoformat(start)
        end_date = datetime.fromisoformat(end)
        
        if start_date >= end_date:
            raise HTTPException(
                status_code=400,
                detail="Start date must be before end date"
            )
        
        # Get historical data
        records = storage.get_historical_data(start_date, end_date)
        
        return {
            "start_date": start,
            "end_date": end,
            "count": len(records),
            "records": records
        }
        
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid date format. Use ISO format (YYYY-MM-DD)"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }


@router.post("/api/batch-analyze", response_model=BatchAnalyzeResponse)
async def batch_analyze(request: BatchAnalyzeRequest):
    """
    Analyze multiple texts in batch mode
    
    Example:
    ```
    POST /api/batch-analyze
    {
        "texts": ["Text 1", "Text 2", "Text 3", ...]
    }
    ```
    """
    try:
        if not request.texts:
            raise HTTPException(status_code=400, detail="Texts list cannot be empty")
        
        if len(request.texts) > 1000:
            raise HTTPException(status_code=400, detail="Maximum 1000 texts per batch")
        
        # Process batch
        result = batch_processor.process_large_dataset(request.texts)
        
        return BatchAnalyzeResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/stream-analyze", response_model=StreamAnalyzeResponse)
async def stream_analyze(request: StreamAnalyzeRequest):
    """
    Analyze text in stream mode (optimized for real-time processing)
    
    Example:
    ```
    POST /api/stream-analyze
    {
        "text": "This is amazing!",
        "metadata": {"source": "twitter", "user_id": "123"}
    }
    ```
    """
    try:
        if not request.text:
            raise HTTPException(status_code=400, detail="Text cannot be empty")
        
        # Process stream item
        result = stream_processor.process_stream_item(request.text, request.metadata)
        
        return StreamAnalyzeResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/batch-stats")
async def get_batch_stats():
    """Get batch processing statistics"""
    try:
        stats = batch_processor.get_stats()
        return {
            "processing_mode": "batch",
            "stats": stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/stream-stats")
async def get_stream_stats():
    """Get stream processing statistics"""
    try:
        overall_stats = stream_processor.get_stats()
        window_stats = stream_processor.get_window_statistics()
        
        return {
            "processing_mode": "stream",
            "overall_stats": overall_stats,
            "window_stats": window_stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/compare-processing")
async def compare_processing(request: BatchAnalyzeRequest):
    """
    Run comparison between batch and stream processing
    
    Example:
    ```
    POST /api/compare-processing
    {
        "texts": ["Text 1", "Text 2", ...]
    }
    ```
    """
    try:
        if not request.texts:
            raise HTTPException(status_code=400, detail="Texts list cannot be empty")
        
        if len(request.texts) > 500:
            raise HTTPException(status_code=400, detail="Maximum 500 texts for comparison")
        
        # Run comparison
        results = comparison_framework.run_comparison(request.texts)
        flow_data = comparison_framework.get_flow_chart_data()
        
        return {
            "comparison": results['comparison'],
            "flow_data": flow_data,
            "batch_results": {
                "total_items": len(results['batch']['results']),
                "statistics": results['batch']['statistics']
            },
            "stream_results": {
                "total_items": len(results['stream']['results']),
                "statistics": results['stream']['statistics']
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
