# 🚀 Deployment Guide

Complete guide to deploying your Rewarding English Learning App to production.

## Deployment Architecture

```
┌─────────────────────────────────────────────────────┐
│                    Vercel (Frontend)                │
│                 Next.js + TypeScript                │
│              Automatic CI/CD Pipeline               │
└──────────────────────┬──────────────────────────────┘
                       │ HTTPS API Calls
                       │
┌──────────────────────▼──────────────────────────────┐
│          Railway/Heroku/DigitalOcean                │
│              Flask + Gunicorn + PostgreSQL          │
│           Database: PostgreSQL (Production)         │
└─────────────────────────────────────────────────────┘
```

## Backend Deployment

### Step 1: Prepare Backend for Production

1. **Upgrade to PostgreSQL** in `backend/pyproject.toml`:
   ```toml
   dependencies = [
       "flask==3.0.0",
       "flask-cors==4.0.0",
       "flask-sqlalchemy==3.1.1",
       "sqlalchemy==2.0.25",
       "python-dotenv==1.0.0",
       "psycopg2-binary==2.9.9",  # Add for PostgreSQL
       "gunicorn==21.2.0",         # Add for production server
   ]
   ```

2. **Update `.env` for production**:
   ```
   FLASK_ENV=production
   FLASK_APP=main.py
   DATABASE_URL=postgresql://user:password@db-host:5432/learning_db
   SECRET_KEY=your-super-secret-key-change-this
   ```

3. **Update `main.py`** for production:
   ```python
   from app import create_app
   import os

   app = create_app()

   if __name__ == '__main__':
       # In production, use Gunicorn instead of Flask dev server
       debug = os.getenv('FLASK_ENV') == 'development'
       if not debug:
           # Production: use Gunicorn
           from gunicorn.app.base import BaseApplication
           app.run(debug=False, host='0.0.0.0', port=5000)
       else:
           # Development
           app.run(debug=True, host='0.0.0.0', port=5000)
   ```

### Step 2: Deploy to Railway (Recommended for Beginners)

1. **Create Railway Account**: https://railway.app

2. **Install Railway CLI**:
   ```bash
   npm i -g @railway/cli
   ```

3. **Login to Railway**:
   ```bash
   railway login
   ```

4. **Create `.railwayrc.json`** in project root:
   ```json
   {
     "projectId": "your-project-id",
     "environmentId": "production"
   }
   ```

5. **Create `Procfile`** in `backend/`:
   ```
   web: gunicorn -w 4 -b 0.0.0.0:${PORT:-5000} main:app
   ```

6. **Deploy**:
   ```bash
   cd backend
   railway up
   ```

7. **Add Environment Variables** in Railway Dashboard:
   - `FLASK_ENV=production`
   - `SECRET_KEY=your-secret-key`
   - `DATABASE_URL=your-postgresql-url`

### Step 3: Deploy to Heroku (Alternative)

1. **Create Heroku Account**: https://heroku.com

2. **Install Heroku CLI**: https://devcenter.heroku.com/articles/heroku-cli

3. **Create app**:
   ```bash
   heroku login
   heroku create your-app-name
   ```

4. **Add PostgreSQL**:
   ```bash
   heroku addons:create heroku-postgresql:hobby-dev
   ```

5. **Set environment variables**:
   ```bash
   heroku config:set FLASK_ENV=production
   heroku config:set SECRET_KEY=your-secret-key
   ```

6. **Deploy**:
   ```bash
   cd backend
   git push heroku main
   ```

### Step 4: Deploy to DigitalOcean (Most Control)

1. **Create Droplet** (Ubuntu 22.04, 1GB RAM minimum)

2. **SSH into droplet**:
   ```bash
   ssh root@your-droplet-ip
   ```

3. **Setup environment**:
   ```bash
   apt update && apt upgrade -y
   apt install python3-pip python3-venv postgresql postgresql-contrib nginx -y
   ```

4. **Setup PostgreSQL**:
   ```bash
   sudo -u postgres createdb learning_db
   sudo -u postgres createuser learning_user -P
   ```

5. **Clone and setup**:
   ```bash
   git clone your-repo.git
   cd RewardingLearning/backend
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

6. **Setup Nginx** as reverse proxy:
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;

       location / {
           proxy_pass http://127.0.0.1:5000;
           proxy_set_header Host $host;
       }
   }
   ```

7. **Setup Systemd service**:
   ```ini
   [Unit]
   Description=Rewarding Learning API
   After=network.target

   [Service]
   User=www-data
   WorkingDirectory=/home/your-user/RewardingLearning/backend
   ExecStart=/home/your-user/RewardingLearning/backend/venv/bin/gunicorn -w 4 main:app
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```

## Frontend Deployment

### Step 1: Prepare Frontend

1. **Update `frontend/.env.production`**:
   ```
   NEXT_PUBLIC_API_URL=https://your-api-domain.com/api
   ```

2. **Build locally to test**:
   ```bash
   cd frontend
   npm run build
   npm run start
   ```

### Step 2: Deploy to Vercel (Recommended)

1. **Create Vercel Account**: https://vercel.com

2. **Import Project**:
   - Go to Vercel Dashboard
   - Click "New Project"
   - Import your GitHub repository
   - Select `frontend` as root directory

3. **Configure Environment Variables**:
   - Add `NEXT_PUBLIC_API_URL` with your backend URL
   - Example: `https://api.yourdomain.com/api`

4. **Deploy**:
   - Vercel auto-deploys on push to main
   - Your app is live at `your-project.vercel.app`

### Step 3: Deploy to Netlify (Alternative)

1. **Create Netlify Account**: https://netlify.com

2. **Connect GitHub** and authorize

3. **Configure Build Settings**:
   - Build command: `npm run build`
   - Publish directory: `.next`
   - Functions directory: leave empty

4. **Add Environment Variables**:
   - `NEXT_PUBLIC_API_URL=https://your-api.com/api`

5. **Deploy**: Automatic on git push

### Step 4: Custom Domain Setup

1. **Register Domain**: GoDaddy, Namecheap, or your registrar

2. **Point DNS to Vercel**:
   - In Vercel Dashboard: Settings > Domains
   - Add your custom domain
   - Update DNS records as shown

3. **Enable SSL Certificate**: Automatic with Vercel

## Database Backup & Maintenance

### PostgreSQL Backups

```bash
# Manual backup
pg_dump learning_db > backup.sql

# Restore from backup
psql learning_db < backup.sql

# Automated daily backups (Linux cron)
0 2 * * * pg_dump learning_db > /backups/learning_db_$(date +\%Y\%m\%d).sql
```

### Monitor Database Performance

```bash
# Connect to PostgreSQL
psql -d learning_db

# List all tables
\dt

# View table size
SELECT schemaname, tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename))
FROM pg_tables
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

## SSL/HTTPS Configuration

### Automatic (Recommended with Vercel)
Vercel automatically provisions and renews SSL certificates.

### Manual (with Let's Encrypt on DigitalOcean)
```bash
apt install certbot python3-certbot-nginx -y
certbot certonly --nginx -d your-domain.com
```

## Monitoring & Logging

### Backend Logging

```python
# In app/__init__.py
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### Monitor with New Relic/Datadog
- Add New Relic APM for Python
- Monitor API response times
- Track error rates
- Set up alerts

## Security Checklist

- [ ] Change `SECRET_KEY` to a unique, strong value
- [ ] Set `FLASK_ENV=production`
- [ ] Enable HTTPS/SSL
- [ ] Configure CORS for your domain only
- [ ] Set strong database passwords
- [ ] Enable database backups
- [ ] Keep dependencies updated
- [ ] Use environment variables for secrets
- [ ] Enable rate limiting on API
- [ ] Setup monitoring and alerts
- [ ] Regular security audits

## Performance Optimization

### Backend
```python
# Add caching
from flask_caching import Cache

cache = Cache(app, config={'CACHE_TYPE': 'simple'})

# Cache lesson listings (1 hour)
@app.route('/api/lessons')
@cache.cached(timeout=3600)
def get_lessons():
    ...
```

### Frontend
- Already optimized with Next.js
- Automatic code splitting
- Image optimization
- Static site generation for home page

## Scaling Considerations

1. **Horizontal Scaling**: Add more Gunicorn workers
2. **Caching Layer**: Add Redis for session and data caching
3. **Database**: Use connection pooling with PgBouncer
4. **CDN**: Serve static assets from CloudFlare
5. **Load Balancer**: Add load balancing for multiple backend instances

## Cost Estimation (Monthly)

| Service | Free Tier | Paid Option |
|---------|-----------|------------|
| Vercel Frontend | ✅ Yes | $20-100 |
| Railway Backend | 5GB/month | $10-50 |
| PostgreSQL | - | $15 (Railway) |
| Custom Domain | - | $10-15 |
| **Total** | **Free** | **$35-165** |

## Troubleshooting Deployment

### Backend won't start
```bash
# Check logs
heroku logs --tail

# Verify dependencies
pip list

# Test locally
python main.py
```

### API calls failing from frontend
- Check `NEXT_PUBLIC_API_URL` is correct
- Verify CORS is enabled on backend
- Check browser console for errors

### Database connection errors
- Verify PostgreSQL is running
- Check connection string format
- Verify credentials are correct

## Rollback Procedure

### Vercel
```bash
# View previous deployments
vercel deployments

# Rollback to previous deployment
vercel rollback
```

### Railway
- Use Railway Dashboard to select previous version
- One-click rollback

## Support & Resources

- **Flask Deployment**: https://flask.palletsprojects.com/deployment/
- **Next.js Deployment**: https://nextjs.org/docs/deployment
- **PostgreSQL**: https://www.postgresql.org/docs/
- **Vercel Docs**: https://vercel.com/docs

---

**Deployment Checklist**:
- [ ] Backend code ready for production
- [ ] Frontend environment variables set
- [ ] Database configured and backed up
- [ ] SSL/HTTPS enabled
- [ ] Environment variables configured
- [ ] Monitoring set up
- [ ] Backup strategy in place
- [ ] Security checklist completed
- [ ] Load testing performed
- [ ] Documentation updated

---

*Ready to go live? Follow these steps and your app will be production-ready!* 🚀

