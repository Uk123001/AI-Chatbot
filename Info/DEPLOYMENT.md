# AI Booking Assistant - Deployment Guide

## Table of Contents
1. [Local Development](#local-development)
2. [Docker Deployment](#docker-deployment)
3. [Streamlit Cloud](#streamlit-cloud)
4. [Production Server](#production-server)
5. [Database Options](#database-options)
6. [Security Checklist](#security-checklist)

---

## Local Development

### Prerequisites
- Python 3.8+
- Git
- Virtual environment tool

### Setup

```bash
# Clone repository
git clone <repository-url>
cd ai-booking-assistant

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env with your API keys

# Initialize database
python -c "from models import init_db; init_db()"

# Run application
streamlit run main.py
```

The app will be available at `http://localhost:8501`

---

## Docker Deployment

### Using Docker

```bash
# Build image
docker build -t ai-booking-assistant .

# Run container
docker run -p 8501:8501 \
  -e GROQ_API_KEY=your_key \
  -e LLM_PROVIDER=groq \
  -e SENDER_EMAIL=your_email \
  -e SENDER_PASSWORD=your_password \
  -v $(pwd)/data:/app/data \
  ai-booking-assistant
```

### Using Docker Compose

```bash
# Create .env file with your configuration
cp .env.example .env
# Edit .env with actual values

# Start services
docker-compose up -d

# View logs
docker-compose logs -f app

# Stop services
docker-compose down

# Backup database
docker cp ai-booking-assistant:/app/data/bookings.db ./backup/
```

### Docker Compose with PostgreSQL

Uncomment PostgreSQL service in `docker-compose.yml`:

```bash
# Update .env with PostgreSQL details
DATABASE_URL=postgresql://booking_user:password@postgres:5432/bookings

docker-compose up -d
```

---

## Streamlit Cloud

### Prerequisites
- GitHub account
- Streamlit account
- Repository pushed to GitHub

### Deployment Steps

1. **Push to GitHub**
```bash
git add .
git commit -m "Prepare for deployment"
git push origin main
```

2. **Connect to Streamlit Cloud**
   - Visit [share.streamlit.io](https://share.streamlit.io)
   - Click "New app"
   - Select your GitHub repository
   - Set main file: `main.py`

3. **Configure Secrets**
   - In Streamlit Cloud dashboard, click Settings → Secrets
   - Add environment variables:

```
GROQ_API_KEY=your_key
OPENAI_API_KEY=your_key
GOOGLE_API_KEY=your_key
LLM_PROVIDER=groq
LLM_MODEL=mixtral-8x7b-32768
SENDER_EMAIL=your_email
SENDER_PASSWORD=your_password
ADMIN_PASSWORD=secure_password
```

4. **Deploy**
   - Streamlit automatically deploys on push
   - View logs in Streamlit Cloud dashboard

### Important Notes
- Streamlit Cloud provides free tier with limitations
- SQLite works but state resets on redeploys
- Use external database for production (see Database Options)
- Viewer restrictions available for Pro plan

---

## Production Server

### Using DigitalOcean/AWS/Azure

#### 1. Server Setup

```bash
# SSH into server
ssh root@your_server_ip

# Update system
apt update && apt upgrade -y

# Install dependencies
apt install -y python3.10 python3-pip python3-venv git nginx

# Clone repository
cd /var/www
git clone <repository-url>
cd ai-booking-assistant

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install packages
pip install -r requirements.txt
```

#### 2. Using Gunicorn + Nginx

```bash
# Install Gunicorn
pip install gunicorn

# Create systemd service file
sudo nano /etc/systemd/system/booking-assistant.service
```

Add:
```ini
[Unit]
Description=AI Booking Assistant
After=network.target

[Service]
User=www-data
WorkingDirectory=/var/www/ai-booking-assistant
Environment="PATH=/var/www/ai-booking-assistant/venv/bin"
ExecStart=/var/www/ai-booking-assistant/venv/bin/streamlit run main.py \
    --server.port=8501 \
    --server.address=127.0.0.1

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable booking-assistant
sudo systemctl start booking-assistant

# Check status
sudo systemctl status booking-assistant
```

#### 3. Configure Nginx

```bash
sudo nano /etc/nginx/sites-available/booking-assistant
```

Add:
```nginx
server {
    listen 80;
    server_name your_domain.com;

    location / {
        proxy_pass http://127.0.0.1:8501;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Websocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/booking-assistant /etc/nginx/sites-enabled/

# Test nginx config
sudo nginx -t

# Restart nginx
sudo systemctl restart nginx
```

#### 4. SSL Certificate (Let's Encrypt)

```bash
sudo apt install -y certbot python3-certbot-nginx

sudo certbot --nginx -d your_domain.com

# Auto-renewal
sudo systemctl enable certbot.timer
```

#### 5. Environment Variables

```bash
# Create .env file
sudo nano /var/www/ai-booking-assistant/.env
# Add all configuration variables

# Fix permissions
sudo chown www-data:www-data .env
sudo chmod 600 .env
```

#### 6. Monitoring

```bash
# View logs
sudo journalctl -u booking-assistant -f

# Monitor memory/CPU
htop

# Check disk space
df -h
```

---

## Database Options

### SQLite (Default - Development Only)

```bash
# No setup required
# Located at: bookings.db
```

**Limitations:**
- Single connection
- Not suitable for multiple concurrent users
- State loss on server restart

### PostgreSQL (Recommended Production)

#### Setup

```bash
# Install PostgreSQL
sudo apt install -y postgresql postgresql-contrib

# Create user and database
sudo sudo -u postgres psql

CREATE USER booking_user WITH PASSWORD 'secure_password';
CREATE DATABASE bookings OWNER booking_user;
ALTER ROLE booking_user SET client_encoding TO 'utf8';
ALTER ROLE booking_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE booking_user SET default_transaction_deferrable TO on;
ALTER ROLE booking_user SET timezone TO 'UTC';

\q
```

#### Update config.py

```python
DATABASE_URL = "postgresql://booking_user:secure_password@localhost:5432/bookings"
```

#### .env file

```
DATABASE_URL=postgresql://booking_user:password@localhost:5432/bookings
```

### Supabase (PostgreSQL + Backend-as-a-Service)

1. Visit [supabase.com](https://supabase.com)
2. Create new project
3. Copy connection string
4. Add to .env: `DATABASE_URL=<connection-string>`

### MongoDB (Alternative)

```bash
# Install pymongo
pip install pymongo

# Update models.py for MongoDB (optional)
```

---

## Security Checklist

### Before Deployment

- [ ] Change default admin password
- [ ] Use environment variables for all secrets
- [ ] Enable HTTPS/SSL
- [ ] Use strong database password
- [ ] Rotate API keys regularly
- [ ] Set up firewall rules
- [ ] Enable logging
- [ ] Regular database backups

### Production Configuration

```bash
# 1. API Key Management
# Never commit .env or secrets.toml
echo ".env" >> .gitignore
echo "secrets.toml" >> .gitignore

# 2. Database
# Use external database (PostgreSQL)
# Regular automated backups
# Strong connection encryption

# 3. Application
# Update admin password in .env
# Set proper CORS headers
# Implement rate limiting

# 4. Email
# Use OAuth2 instead of app passwords (when possible)
# Configure SMTP with TLS
# Test email delivery

# 5. Monitoring
# Set up logging (CloudWatch, ELK, etc.)
# Configure alerts for errors
# Monitor resource usage
# Track booking success rates

# 6. Backups
# Automated daily backups
# Test restore procedures
# Store backups securely
```

### Backup Strategy

```bash
# Daily backup script
#!/bin/bash

BACKUP_DIR="/backups/booking-assistant"
DB_FILE="/var/www/ai-booking-assistant/bookings.db"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Backup database
cp $DB_FILE $BACKUP_DIR/bookings_$DATE.db.gz

# Keep last 30 days
find $BACKUP_DIR -name "*.db.gz" -mtime +30 -delete

# Upload to cloud storage (S3, GCS, etc.)
# aws s3 cp $BACKUP_DIR s3://your-bucket/backups/
```

Add to crontab:
```
0 2 * * * /var/www/ai-booking-assistant/backup.sh
```

### Monitoring Setup

```bash
# Install monitoring tools
pip install prometheus-client

# Enable application metrics logging
# Configure alerting
# Set up dashboards
```

---

## Performance Optimization

### Caching

```python
# In config.py
CACHE_TTL = 3600  # 1 hour

# Implement caching for:
# - Vector store lookups
# - Model inference
# - Database queries
```

### Load Balancing

For high traffic, use:
- Nginx load balancing
- Multiple app instances
- Shared database
- Caching layer (Redis)

### Database Optimization

```sql
-- Add indexes for frequently queried fields
CREATE INDEX idx_booking_date ON bookings(booking_date);
CREATE INDEX idx_booking_type ON bookings(booking_type);
CREATE INDEX idx_customer_email ON customers(email);
CREATE INDEX idx_booking_status ON bookings(status);
```

---

## Troubleshooting

### App Won't Start

```bash
# Check logs
journalctl -u booking-assistant -n 50

# Verify Python environment
source venv/bin/activate
python -c "import streamlit; print(streamlit.__version__)"

# Test imports
python -c "from models import init_db; init_db()"
```

### Database Connection Issues

```bash
# Test connection
psql -U booking_user -d bookings -h localhost

# Check SQLAlchemy connection
python -c "from models import get_session; s = get_session(); print('Connected')"
```

### Email Not Sending

```bash
# Test SMTP configuration
python -c "
import smtplib
server = smtplib.SMTP('smtp.gmail.com', 587)
server.starttls()
server.login('email@gmail.com', 'password')
server.quit()
print('SMTP OK')
"
```

### Memory Issues

```bash
# Monitor memory usage
free -h

# Check Python memory
ps aux | grep python

# Optimize:
# - Reduce MAX_HISTORY
# - Use smaller chunk sizes
# - Clear vector store cache
```

---

## Scaling Strategy

### Phase 1: Single Server (0-100 bookings/day)
- Single Streamlit instance
- SQLite or single PostgreSQL
- Basic monitoring

### Phase 2: Multiple Instances (100-1000 bookings/day)
- Nginx load balancer
- PostgreSQL database
- Redis caching
- Structured logging

### Phase 3: High Scale (1000+ bookings/day)
- Kubernetes orchestration
- Database replication
- Message queue (Celery)
- CDN for static assets
- Microservices architecture

---

## Support & References

- [Streamlit Documentation](https://docs.streamlit.io)
- [LangChain Documentation](https://python.langchain.com)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Docker Documentation](https://docs.docker.com)
- [Nginx Documentation](https://nginx.org/en/docs/)
