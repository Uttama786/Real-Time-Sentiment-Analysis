# Real-Time Sentiment Analysis System

A comprehensive real-time sentiment analysis platform that ingests data from multiple sources, performs sentiment analysis, and provides visualization through an interactive dashboard.

## 🎯 Features

- **Real-time Data Ingestion**: Collect data from multiple sources (RSS feeds, Twitter, custom sources)
- **Advanced Sentiment Analysis**: State-of-the-art NLP models for accurate sentiment classification
- **Batch Processing**: High-throughput parallel processing for large datasets
- **Stream Processing**: Low-latency real-time processing for continuous data streams
- **Processing Comparison**: Framework for comparing batch vs stream performance
- **Interactive Dashboard**: Real-time visualization with Plotly and Dash, including flow charts
- **RESTful API**: Complete FastAPI-based API for integration
- **PostgreSQL Database**: Persistent storage for sentiment records and metadata
- **Queueing**: Uses Redis when available; automatically falls back to an in-memory queue on Windows
- **Scalable Architecture**: Microservices-based design for easy scaling

## 📋 Prerequisites

- **Python**: 3.8 or higher
- **PostgreSQL**: 12 or higher
- **Redis**: 6.0 or higher (optional; on Windows the app auto-falls back to in-memory queue)
- **Docker**: (optional, for containerized deployment)

## 🚀 Quick Start

### Option 1: Manual Installation (Recommended for Development)

#### 1. Clone and Navigate to Project
```bash
cd "path/to/project"
```

#### 2. Create Virtual Environment
```bash
python -m venv .venv
.venv\Scripts\activate  # On Windows
source .venv/bin/activate  # On Linux/Mac
```

#### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

#### 4. Download NLP Models
```bash
python scripts/download_models.py
```

#### 5. Configure Environment
Create or edit `.env` file:
```env
# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=sentiment_db
DB_USER=postgres
DB_PASSWORD=0000

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
```

#### 6. Setup Database
```bash
python scripts/migrate.py
```

#### 7. Start Services

Open 4 separate terminals (in-memory queue will be used automatically on Windows if Redis is not running):

**Terminal 1 - API Server** (Required)
```bash
python app.py
```
Access at: http://localhost:8000

**Terminal 2 - Dashboard** (Optional but recommended)
```bash
python dashboard/app.py
```
Access at: http://localhost:8050

**Terminal 3 - Data Ingestion Service** (Optional)
```bash
python services/ingestion.py
```

**Terminal 4 - Processing Service** (Optional)
```bash
python services/processor.py
```

### Option 2: Docker Deployment

```bash
docker-compose up -d
```

This will start all services including PostgreSQL and Redis.

## 🔑 Data Sources Configuration

The system ingests data from multiple sources for sentiment analysis.

### Default Setup (Recommended for Testing/Academic Projects)

**✅ Works out-of-the-box with:**
- **Sample Twitter Data**: Realistic tweet samples automatically generated
- **Real RSS News Feeds**: Live articles from TechCrunch, HackerNews, The Verge
- **Custom Sources**: Add your own data via API endpoints

Simply start the ingestion service:
```bash
python services/ingestion.py
```

The system will automatically ingest sample tweets + real news articles every cycle.

### Optional: Twitter API Integration (Paid Service)

⚠️ **Important Twitter API Limitations:**
- **Free Tier**: NO keyword search access (returns 402 Payment Required)
- **Basic Tier**: $100/month (10K tweets/month, keyword search enabled)
- **Pro Tier**: $5,000/month (1M tweets/month)

**For academic projects and demos**, sample data is recommended as it:
- ✅ Demonstrates full system functionality
- ✅ Shows realistic sentiment analysis
- ✅ Saves $100/month in API costs
- ✅ Avoids rate limits and quota issues

**Only configure Twitter API if you have a paid account:**

1. **Get Twitter API Credentials** (see [API_KEYS_QUICKSTART.md](API_KEYS_QUICKSTART.md))
   - Requires Twitter Developer Account with paid subscription
   - Get Bearer Token from Developer Portal
   - Add to `.env`: `TWITTER_BEARER_TOKEN=your_token_here`

2. **Enable in Configuration**
   
   Edit `config/sources.yaml`:
   ```yaml
   twitter:
     enabled: true
     keywords:
       - "product review"  # Minimal keywords to save API credits
     max_tweets: 10
     fetch_replies: false  # Disable to reduce API calls
     polling_interval: 3600  # 1 hour to avoid rate limits
   ```

3. **Test Your Setup**
   ```bash
   python scripts/test_social_media_api.py
   ```

### What Data You Get

- **Sample Twitter Data**: 
  - Realistic tweets with sentiment variety
  - Multiple keywords coverage
  - Author information and timestamps
  - Perfect for demos and testing

- **Real RSS News**: 
  - Live technology news articles
  - Updated every polling cycle
  - Diverse sentiment examples

**Note**: The system architecture and processing pipeline work identically with sample or real Twitter data—only the data source differs.

## 📡 API Endpoints

### Core Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | API information |
| `POST` | `/api/analyze` | Analyze sentiment of text |
| `GET` | `/api/sentiments` | Get sentiment records |
| `GET` | `/api/stats` | Get statistics |
| `GET` | `/api/history` | Get historical data |

### Batch & Stream Processing Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/batch-analyze` | Process multiple texts in batch mode |
| `POST` | `/api/stream-analyze` | Process single text in stream mode |
| `POST` | `/api/compare-processing` | Compare batch vs stream performance |
| `GET` | `/api/batch-stats` | Get batch processing statistics |
| `GET` | `/api/stream-stats` | Get stream processing statistics |

### Example Usage

**Analyze Sentiment:**
```bash
curl -X POST "http://localhost:8000/api/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "I love this product! It is amazing.",
    "source": "user_input"
  }'
```

**Get Statistics:**
```bash
curl "http://localhost:8000/api/stats"
```

**Batch Process Multiple Texts:**
```bash
curl -X POST "http://localhost:8000/api/batch-analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "texts": [
      "I love this product!",
      "This is terrible.",
      "It is okay."
    ]
  }'
```

**Stream Process Single Text:**
```bash
curl -X POST "http://localhost:8000/api/stream-analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Amazing experience!",
    "metadata": {"source": "twitter"}
  }'
```

**Compare Processing Methods:**
```bash
curl -X POST "http://localhost:8000/api/compare-processing" \
  -H "Content-Type: application/json" \
  -d '{
    "texts": ["text1", "text2", "text3", ...]
  }'
```

## 📊 Dashboard

The interactive dashboard provides:
- **Total Records**: Overall count of analyzed sentiments
- **Sentiment Distribution**: Pie chart showing positive/negative/neutral breakdown
- **Sentiment Over Time**: Time-series chart of sentiment trends
- **Source Distribution**: Analysis by data source
- **Recent Sentiments**: Latest analyzed records

### Batch vs Stream Processing Comparison
- **Interactive Comparison Test**: Run performance comparison with one click
- **Processing Flow Charts**: Visual representation of batch and stream workflows
- **Performance Metrics**: Throughput, latency, and time comparisons
- **Detailed Comparison Table**: Side-by-side analysis of both methods
- **Real-time Results**: Live visualization of comparison results

Access at: http://localhost:8050

## 🏗️ Project Structure

```
├── api/                          # FastAPI routes and middleware
│   ├── routes.py                # API endpoints
│   └── middleware.py            # Request/response middleware
├── config/                       # Configuration files
│   ├── models.yaml              # Model configurations
│   └── sources.yaml             # Data source configurations
├── dashboard/                    # Dash dashboard application
│   └── app.py                   # Dashboard UI
├── models/                       # Machine learning models
│   ├── database.py              # SQLAlchemy ORM models
│   ├── preprocessor.py          # Text preprocessing
│   ├── sentiment_model.py       # Sentiment analysis model
│   ├── batch_processor.py       # Batch processing model
│   ├── stream_processor.py      # Stream processing model
│   ├── processing_comparison.py # Comparison framework
│   └── __pycache__/             # Python cache
├── scripts/                      # Utility scripts
│   ├── download_models.py       # Download NLP models
│   └── migrate.py               # Database migration
├── services/                     # Microservices
│   ├── ingestion.py             # Data ingestion service
│   ├── processor.py             # Sentiment processing service
│   └── storage.py               # Database storage service
├── tests/                        # Unit tests
│   ├── test_api.py
│   ├── test_ingestion.py
│   ├── test_processor.py
│   └── test_batch_stream.py     # Batch/stream tests
├── app.py                        # Main FastAPI application
├── requirements.txt              # Python dependencies
├── docker-compose.yml            # Docker orchestration
├── Dockerfile                    # Container definition
├── .env                          # Environment variables
├── .gitignore                    # Git ignore rules
├── BATCH_STREAM_COMPARISON.md    # Batch/stream feature docs
├── IMPLEMENTATION_SUMMARY.md     # Implementation details
└── README.md                     # This file
```

## 🔧 Configuration

### Database Configuration
Edit `.env` to configure PostgreSQL connection:
```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=sentiment_db
DB_USER=postgres
DB_PASSWORD=your_password
```

### Data Sources
Edit `config/sources.yaml` to add/modify data sources:
```yaml
sources:
  twitter:
    enabled: true
    api_key: "your_api_key"
  rss_feeds:
    - url: "https://example.com/feed"
      name: "Example Feed"
```

### Models
Edit `config/models.yaml` to configure NLP models:
```yaml
models:
  primary: "transformers"
  fallback: "vader"
  cache_size: 1000
```

## 📦 Dependencies

### Core
- **FastAPI** - Modern web framework
- **SQLAlchemy** - ORM for database operations
- **PostgreSQL** - Primary database
- **Redis** - Message queue

### NLP
- **transformers** - State-of-the-art NLP models
- **nltk** - Natural Language Toolkit
- **spacy** - Industrial-strength NLP
- **textblob** - Simple API for NLP tasks
- **vaderSentiment** - Lexicon-based sentiment analysis

### Visualization
- **Dash** - Interactive dashboards
- **Plotly** - Charting library
- **dash-bootstrap-components** - UI components

### Data Processing
- **pandas** - Data manipulation
- **numpy** - Numerical computing
- **feedparser** - RSS feed parsing
- **beautifulsoup4** - HTML parsing

## 🧪 Testing

Run tests with pytest:
```bash
pytest tests/
```

Run tests with coverage:
```bash
pytest --cov=. tests/
```

Run batch/stream processing tests:
```bash
python tests/test_batch_stream.py
```

## 🐛 Troubleshooting

### Twitter API Errors

**Problem**: `402 Payment Required - Your enrolled account does not have any credits`

**Explanation**: Twitter Free tier doesn't support keyword search. Requires Basic ($100/mo) or higher.

**Solution**: 
- ✅ **Recommended**: Use sample data (already working)
- Or upgrade to Twitter Basic tier ($100/month)
- System continues to work with sample tweets + real news feeds

**Problem**: `429 Too Many Requests`

**Solution**: Reduce polling frequency in `config/sources.yaml`:
```yaml
polling_interval: 3600  # 1 hour instead of 60 seconds
```

### PostgreSQL Connection Error
**Problem**: `FATAL: password authentication failed for user "postgres"`

**Solution**:
1. Verify PostgreSQL is running
2. Check database credentials in `.env`
3. Reset PostgreSQL password if needed

### Redis Connection Error
**Problem**: `Error 10061 connecting to localhost:6379`

**Solution**:
1. Start Redis: `docker run -d -p 6379:6379 redis:7-alpine`
2. Or install Redis locally for Windows
3. Check `REDIS_HOST` and `REDIS_PORT` in `.env`

### Module Not Found Error
**Problem**: `ModuleNotFoundError: No module named 'sqlalchemy'`

**Solution**:
1. Activate virtual environment: `.venv\Scripts\activate`
2. Reinstall dependencies: `pip install -r requirements.txt`

### Port Already in Use
**Problem**: `Address already in use`

**Solution**:
```bash
# Find process using port 8000
netstat -ano | findstr :8000
# Kill process (replace PID)
taskkill /PID <PID> /F
```

## 📈 Performance Tips

1. **Database Indexing**: Ensure timestamp columns are indexed
2. **Connection Pooling**: Configure SQLAlchemy connection pool size
3. **Redis Caching**: Enable Redis for improved performance
4. **Batch Processing**: Use batch mode for large datasets (>100 items) for high throughput
5. **Stream Processing**: Use stream mode for real-time analysis with low latency
6. **Processing Selection**: Choose batch for historical analysis, stream for live monitoring
7. **Model Optimization**: Use quantized models for faster inference
8. **Parallel Workers**: Configure batch processor workers based on CPU cores

## 🔒 Security Recommendations

- Use environment variables for sensitive data
- Enable HTTPS in production
- Implement API authentication
- Use strong database passwords
- Regularly update dependencies
- Implement rate limiting on API endpoints

## 📝 License

This project is part of M.Tech Data Stream Mining coursework.

## 👥 Contributing

For contributions and improvements:
1. Create a feature branch
2. Make your changes
3. Write tests
4. Submit a pull request

## 📧 Support

For issues and questions:
1. Check the troubleshooting section
2. Review API documentation at `/docs`
3. Check test files for usage examples

## 📚 Additional Resources

### Documentation
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Dash Documentation](https://dash.plotly.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Transformers Documentation](https://huggingface.co/docs/transformers/)

### Project Documentation
- [Batch vs Stream Comparison Guide](BATCH_STREAM_COMPARISON.md) - Complete feature documentation
- [Implementation Summary](IMPLEMENTATION_SUMMARY.md) - Technical implementation details
- API Documentation: http://localhost:8000/docs (when server is running)

---

**Last Updated**: January 2026
**Python Version**: 3.8+
**Status**: Active Development
