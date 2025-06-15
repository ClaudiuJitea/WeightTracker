# 🚀 Deployment Guide for HealthTracker

This guide provides detailed instructions for deploying HealthTracker in various environments.

## 📋 Prerequisites

- Python 3.8 or higher
- Git
- A web server (for production)
- Database server (optional, for production)

## 🔧 Environment Setup

### Development Environment

1. **Clone the repository**
   ```bash
   git clone https://github.com/ClaudiuJitea/WeightTracker.git
   cd WeightTracker
   ```

2. **Create virtual environment**
   ```bash
   python -m venv myenv
   
   # Windows
   myenv\Scripts\activate
   
   # macOS/Linux
   source myenv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` file:
   ```env
   FLASK_APP=run.py
   FLASK_DEBUG=1
   SECRET_KEY=your-development-secret-key
   ```

5. **Initialize database**
   ```bash
   flask db upgrade
   ```

6. **Create admin user**
   ```bash
   python create_admin.py
   ```

7. **Run development server**
   ```bash
   python run.py
   ```

### Production Environment

#### Option 1: Traditional Server Deployment

1. **Server Setup**
   ```bash
   # Update system
   sudo apt update && sudo apt upgrade -y
   
   # Install Python and dependencies
   sudo apt install python3 python3-pip python3-venv nginx supervisor postgresql postgresql-contrib
   ```

2. **Database Setup (PostgreSQL)**
   ```bash
   sudo -u postgres psql
   CREATE DATABASE healthtrack;
   CREATE USER healthtrack_user WITH PASSWORD 'your_password';
   GRANT ALL PRIVILEGES ON DATABASE healthtrack TO healthtrack_user;
   \q
   ```

3. **Application Setup**
   ```bash
   # Clone repository
   cd /var/www
   sudo git clone https://github.com/ClaudiuJitea/WeightTracker.git
   sudo chown -R www-data:www-data WeightTracker
   cd WeightTracker
   
   # Create virtual environment
   sudo -u www-data python3 -m venv venv
   sudo -u www-data venv/bin/pip install -r requirements.txt
   sudo -u www-data venv/bin/pip install gunicorn psycopg2-binary
   ```

4. **Environment Configuration**
   ```bash
   sudo -u www-data cp .env.example .env
   sudo -u www-data nano .env
   ```
   
   Production `.env`:
   ```env
   FLASK_APP=run.py
   FLASK_DEBUG=0
   SECRET_KEY=your-super-secret-production-key
   DATABASE_URL=postgresql://healthtrack_user:your_password@localhost/healthtrack
   ```

5. **Database Migration**
   ```bash
   sudo -u www-data venv/bin/flask db upgrade
   sudo -u www-data venv/bin/python create_admin.py
   ```

6. **Gunicorn Configuration**
   
   Create `/etc/supervisor/conf.d/healthtrack.conf`:
   ```ini
   [program:healthtrack]
   command=/var/www/WeightTracker/venv/bin/gunicorn -w 4 -b 127.0.0.1:8000 run:app
   directory=/var/www/WeightTracker
   user=www-data
   autostart=true
   autorestart=true
   redirect_stderr=true
   stdout_logfile=/var/log/healthtrack.log
   environment=PATH="/var/www/WeightTracker/venv/bin"
   ```

7. **Nginx Configuration**
   
   Create `/etc/nginx/sites-available/healthtrack`:
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;
       
       location / {
           proxy_pass http://127.0.0.1:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }
       
       location /static {
           alias /var/www/WeightTracker/app/static;
           expires 1y;
           add_header Cache-Control "public, immutable";
       }
   }
   ```

8. **Enable and Start Services**
   ```bash
   sudo ln -s /etc/nginx/sites-available/healthtrack /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl reload nginx
   sudo supervisorctl reread
   sudo supervisorctl update
   sudo supervisorctl start healthtrack
   ```

#### Option 2: Docker Deployment

1. **Create Dockerfile**
   ```dockerfile
   FROM python:3.9-slim
   
   WORKDIR /app
   
   # Install system dependencies
   RUN apt-get update && apt-get install -y \
       gcc \
       && rm -rf /var/lib/apt/lists/*
   
   # Copy requirements and install Python dependencies
   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt
   RUN pip install gunicorn psycopg2-binary
   
   # Copy application code
   COPY . .
   
   # Create non-root user
   RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
   USER appuser
   
   EXPOSE 5000
   
   CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "run:app"]
   ```

2. **Create docker-compose.yml**
   ```yaml
   version: '3.8'
   
   services:
     web:
       build: .
       ports:
         - "5000:5000"
       environment:
         - FLASK_APP=run.py
         - FLASK_DEBUG=0
         - SECRET_KEY=your-secret-key
         - DATABASE_URL=postgresql://healthtrack:password@db:5432/healthtrack
       depends_on:
         - db
       volumes:
         - ./migrations:/app/migrations
   
     db:
       image: postgres:13
       environment:
         - POSTGRES_DB=healthtrack
         - POSTGRES_USER=healthtrack
         - POSTGRES_PASSWORD=password
       volumes:
         - postgres_data:/var/lib/postgresql/data
   
   volumes:
     postgres_data:
   ```

3. **Deploy with Docker**
   ```bash
   docker-compose up -d
   docker-compose exec web flask db upgrade
   docker-compose exec web python create_admin.py
   ```

#### Option 3: Cloud Platform Deployment

##### Heroku Deployment

1. **Install Heroku CLI**
   ```bash
   # Follow instructions at https://devcenter.heroku.com/articles/heroku-cli
   ```

2. **Prepare for Heroku**
   
   Create `Procfile`:
   ```
   web: gunicorn run:app
   release: flask db upgrade
   ```
   
   Update `requirements.txt` to include:
   ```
   gunicorn
   psycopg2-binary
   ```

3. **Deploy to Heroku**
   ```bash
   heroku create your-app-name
   heroku addons:create heroku-postgresql:hobby-dev
   heroku config:set FLASK_APP=run.py
   heroku config:set FLASK_DEBUG=0
   heroku config:set SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")
   
   git add .
   git commit -m "Deploy to Heroku"
   git push heroku main
   
   heroku run python create_admin.py
   heroku open
   ```

## 🔒 Security Considerations

### Production Security Checklist

- [ ] Change default SECRET_KEY
- [ ] Use HTTPS (SSL/TLS certificates)
- [ ] Set up firewall rules
- [ ] Use strong database passwords
- [ ] Enable database connection encryption
- [ ] Set up regular backups
- [ ] Configure log monitoring
- [ ] Update dependencies regularly
- [ ] Use environment variables for sensitive data
- [ ] Set up rate limiting

### SSL/HTTPS Setup

1. **Using Let's Encrypt (Certbot)**
   ```bash
   sudo apt install certbot python3-certbot-nginx
   sudo certbot --nginx -d your-domain.com
   ```

2. **Update Nginx configuration for HTTPS**
   ```nginx
   server {
       listen 443 ssl http2;
       server_name your-domain.com;
       
       ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
       ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
       
       # SSL configuration
       ssl_protocols TLSv1.2 TLSv1.3;
       ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
       ssl_prefer_server_ciphers off;
       
       location / {
           proxy_pass http://127.0.0.1:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }
   }
   
   server {
       listen 80;
       server_name your-domain.com;
       return 301 https://$server_name$request_uri;
   }
   ```

## 📊 Monitoring and Maintenance

### Log Management

1. **Application Logs**
   ```bash
   # View Gunicorn logs
   sudo tail -f /var/log/healthtrack.log
   
   # View Nginx logs
   sudo tail -f /var/log/nginx/access.log
   sudo tail -f /var/log/nginx/error.log
   ```

2. **Log Rotation**
   
   Create `/etc/logrotate.d/healthtrack`:
   ```
   /var/log/healthtrack.log {
       daily
       missingok
       rotate 52
       compress
       delaycompress
       notifempty
       create 644 www-data www-data
       postrotate
           supervisorctl restart healthtrack
       endscript
   }
   ```

### Database Backup

1. **PostgreSQL Backup Script**
   ```bash
   #!/bin/bash
   # backup_db.sh
   
   BACKUP_DIR="/var/backups/healthtrack"
   DATE=$(date +%Y%m%d_%H%M%S)
   
   mkdir -p $BACKUP_DIR
   
   pg_dump -h localhost -U healthtrack_user healthtrack > $BACKUP_DIR/healthtrack_$DATE.sql
   
   # Keep only last 30 days of backups
   find $BACKUP_DIR -name "healthtrack_*.sql" -mtime +30 -delete
   ```

2. **Schedule with Cron**
   ```bash
   # Add to crontab
   0 2 * * * /path/to/backup_db.sh
   ```

### Updates and Maintenance

1. **Application Updates**
   ```bash
   cd /var/www/WeightTracker
   sudo -u www-data git pull origin main
   sudo -u www-data venv/bin/pip install -r requirements.txt
   sudo -u www-data venv/bin/flask db upgrade
   sudo supervisorctl restart healthtrack
   ```

2. **System Updates**
   ```bash
   sudo apt update && sudo apt upgrade -y
   sudo systemctl restart nginx
   ```

## 🆘 Troubleshooting

### Common Issues

1. **Database Connection Errors**
   - Check database credentials in `.env`
   - Verify database server is running
   - Check firewall settings

2. **Static Files Not Loading**
   - Verify Nginx static file configuration
   - Check file permissions
   - Clear browser cache

3. **Application Won't Start**
   - Check Gunicorn logs
   - Verify virtual environment activation
   - Check Python dependencies

4. **Performance Issues**
   - Monitor server resources
   - Check database query performance
   - Consider adding caching
   - Scale Gunicorn workers

### Health Checks

1. **Application Health**
   ```bash
   curl -f http://localhost:8000/ || echo "Application down"
   ```

2. **Database Health**
   ```bash
   sudo -u postgres psql -c "SELECT 1;" healthtrack
   ```

3. **Service Status**
   ```bash
   sudo supervisorctl status healthtrack
   sudo systemctl status nginx
   ```

## 📞 Support

For deployment issues:
1. Check the application logs
2. Review this deployment guide
3. Create an issue on GitHub with detailed error information
4. Include system information and configuration details

---

**Happy Deploying! 🚀**