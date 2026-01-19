# Deployment Guide

## Quick Deploy to Render.com (Free)

### Prerequisites
- GitHub repository (✓ Already set up)
- Render.com account (free)

### Steps

1. **Sign up on Render.com**
   - Go to https://render.com
   - Sign up with your GitHub account

2. **Create New Blueprint**
   - Click "New" → "Blueprint"
   - Connect your GitHub repository: `Uttama786/Real-Time-Sentiment-Analysis`
   - Render will automatically detect `render.yaml`

3. **Deploy**
   - Click "Apply"
   - Wait 5-10 minutes for deployment
   - Get your live URLs:
     - API: `https://sentiment-api.onrender.com/docs`
     - Dashboard: `https://sentiment-dashboard.onrender.com`

### Environment Variables (Auto-configured)
- PostgreSQL database (free tier)
- Redis cache (free tier)
- All connections handled automatically

---

## Alternative: AWS Deployment

### Prerequisites
- AWS Account with proper IAM permissions
- Docker Desktop installed
- AWS CLI configured

### Required IAM Permissions
Your AWS user needs these policies:
- `AmazonEC2ContainerRegistryFullAccess`
- `AmazonECS_FullAccess`
- `AmazonRDSFullAccess`
- `ElastiCacheFullAccess`

### Steps

1. **Add IAM Permissions**
   ```
   AWS Console → IAM → Users → RealTimeSentimentAnalysis
   → Permissions → Add permissions → Attach policies
   ```

2. **Create ECR Repository**
   ```bash
   aws ecr create-repository --repository-name sentiment-analysis --region us-east-1
   ```

3. **Login to ECR**
   ```bash
   aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 158259501472.dkr.ecr.us-east-1.amazonaws.com
   ```

4. **Build and Push Docker Image**
   ```bash
   docker build -t sentiment-analysis .
   docker tag sentiment-analysis:latest 158259501472.dkr.ecr.us-east-1.amazonaws.com/sentiment-analysis:latest
   docker push 158259501472.dkr.ecr.us-east-1.amazonaws.com/sentiment-analysis:latest
   ```

5. **Create RDS PostgreSQL**
   ```bash
   aws rds create-db-instance \
     --db-instance-identifier sentiment-postgres \
     --db-instance-class db.t3.micro \
     --engine postgres \
     --master-username postgres \
     --master-user-password your-secure-password \
     --allocated-storage 20 \
     --publicly-accessible
   ```

6. **Create ElastiCache Redis**
   ```bash
   aws elasticache create-cache-cluster \
     --cache-cluster-id sentiment-redis \
     --cache-node-type cache.t3.micro \
     --engine redis \
     --num-cache-nodes 1
   ```

7. **Deploy to ECS** (requires additional setup)

---

## Cost Comparison

| Platform | Cost | Setup Time | Difficulty |
|----------|------|------------|------------|
| **Render.com** | Free | 5 minutes | Easy ⭐ |
| **AWS Free Tier** | Free (12 months) | 30+ minutes | Hard ⭐⭐⭐ |
| **Heroku** | Free (limited) | 10 minutes | Medium ⭐⭐ |

---

## Recommended: Start with Render.com

For your M.Tech project, I recommend **Render.com** because:
- ✅ Completely free
- ✅ Automatic HTTPS
- ✅ Auto-deploys from GitHub
- ✅ Managed PostgreSQL + Redis
- ✅ No AWS permissions needed
- ✅ Perfect for academic projects

You can always migrate to AWS later if needed!
