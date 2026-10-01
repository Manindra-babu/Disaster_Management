# RESQ | Production Deployment Guide

This guide covers deployment procedures for **RESQ (Intelligent Disaster Response Coordination Platform)** across containerized environments, cloud platforms, and virtual private servers (VPS).

---

## 1. Architecture Overview

```
                      Internet / Emergency Personnel
                                    │
                                    ▼
                ┌───────────────────────────────────────┐
                │       Reverse Proxy / TLS (Nginx)     │
                │        Port 80 (HTTP) / 443 (HTTPS)   │
                └───────┬───────────────────────┬───────┘
                        │                       │
      / (SPA Static Files)                      │ /api, /ws (Reverse Proxy)
                        ▼                       ▼
            ┌───────────────────────┐   ┌───────────────────────┐
            │   Frontend Container  │   │   Backend Container   │
            │   (Vite + React 19)   │   │   (FastAPI + Uvicorn) │
            │   Port 80             │   │   Port 8000           │
            └───────────────────────┘   └───────────┬───────────┘
                                                    │
                                                    ▼
                                        ┌───────────────────────┐
                                        │  PostgreSQL Database  │
                                        │  Port 5432            │
                                        └───────────────────────┘
```

---

## 2. Pre-Flight Readiness Verification

Before running deployment commands, run the pre-flight verification script on the target host:

```bash
# Set PYTHONPATH and execute pre-flight checker
python scripts/preflight_check.py
```

The script verifies:
1. Environment variables and JWT secret integrity.
2. PostgreSQL/SQLite connection, schema creation, and authoritative seed data.
3. Google Gemini API connectivity (`gemini-3.8-flash`) and deterministic engine fallback.
4. Frontend production build artifacts (`frontend/dist/index.html` and bundled assets).
5. Dockerfiles, Compose files, and Nginx configurations.

---

## 3. Deployment Methods

### Option A: Docker Compose (Recommended for VPS, Cloud VM, Dedicated Server)

**Target Platforms:** Ubuntu 22.04/24.04, AWS EC2, DigitalOcean Droplet, Hetzner Cloud, Linode.

#### Step 1: Install Docker & Docker Compose
```bash
# Ubuntu/Debian
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
```

#### Step 2: Clone Repository & Prepare Environment
```bash
git clone <YOUR_REPOSITORY_URL> resq
cd resq

# Copy production environment configuration
cp .env.production .env

# (Optional) Generate and set a custom random JWT secret
python3 -c "import secrets; print(secrets.token_hex(32))"
# Paste generated key into .env under SECRET_KEY
```

#### Step 3: Build & Launch Containers
```bash
docker compose up -d --build
```

#### Step 4: Verify Deployment Health
```bash
# Check running containers
docker compose ps

# Check backend health
curl http://localhost:8000/health
# Response: {"status":"healthy","platform":"RESQ ...","database":"connected","gemini_configured":true}

# View container logs
docker compose logs -f backend
```

Access the application at `http://<SERVER_IP>:3000` (or Port 80 via Host Nginx).

---

### Option B: Host Nginx & Free SSL (Let's Encrypt)

To serve RESQ securely over standard HTTPS (`https://resq.yourdomain.org`):

#### 1. Install Certbot & Nginx
```bash
sudo apt update
sudo apt install -y nginx certbot python3-certbot-nginx
```

#### 2. Create Nginx Site Configuration
Create `/etc/nginx/sites-available/resq`:
```nginx
server {
    server_name resq.yourdomain.org;

    # Frontend SPA
    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Backend REST API
    location /api/ {
        proxy_pass http://127.0.0.1:8000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # WebSocket Real-Time Stream
    location /ws {
        proxy_pass http://127.0.0.1:8000/ws;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }
}
```

#### 3. Enable Site & Generate SSL Certificate
```bash
sudo ln -s /etc/nginx/sites-available/resq /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
sudo certbot --nginx -d resq.yourdomain.org
```

---

### Option C: Cloud PaaS (Render 1-Click Blueprint)

1. Push your repository to GitHub or GitLab.
2. In the **Render Dashboard**, click **New +** $\rightarrow$ **Blueprint**.
3. Select your repository. Render automatically reads `render.yaml`:
   - Provisions a managed **PostgreSQL** instance (`resq-db`).
   - Builds and starts the **Backend FastAPI Service** (`resq-backend`).
   - Builds and deploys the **Frontend Static Site** (`resq-frontend`).
4. Set the environment variable `GEMINI_API_KEY` in the Render dashboard.

---

### Option D: Decoupled (Vercel Frontend + Railway/Render Backend)

#### 1. Backend on Railway / Render
- Create a new project and connect your GitHub repo.
- Add a PostgreSQL database plugin.
- Set the start command:
  ```bash
  uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT
  ```
- Set environment variables:
  - `DATABASE_URL`: Your PostgreSQL connection string (prefixed with `postgresql+asyncpg://`)
  - `SECRET_KEY`: High-entropy 64-character string
  - `GEMINI_API_KEY`: Your Google Gemini API Key
  - `GEMINI_MODEL`: `gemini-3.8-flash`
  - `PYTHONPATH`: `.`

#### 2. Frontend on Vercel
- Import your repository on [Vercel](https://vercel.com).
- Root Directory: `frontend`
- Framework Preset: `Vite`
- Build Command: `npm run build`
- Output Directory: `dist`
- Environment Variables:
  - `VITE_API_URL`: `https://your-backend-service.up.railway.app`
  - `VITE_WS_URL`: `wss://your-backend-service.up.railway.app/ws`
- `frontend/vercel.json` already contains the SPA routing rewrite rule.

---

## 4. Default Production Credentials

Initial database seed automatically provisions the following default users:

| Email | Password | Role | Permissions |
| :--- | :--- | :--- | :--- |
| `commander@resq.gov.in` | `Commander@123` | `INCIDENT_COMMANDER` | Full dispatch approval, simulation controls, resource command |
| `operator@resq.gov.in` | `Operator@123` | `OPERATOR` | Incident triage, resource editing, plan generation |
| `viewer@resq.gov.in` | `Viewer@123` | `VIEWER` | Read-only access to GIS map and operational telemetry |

> [!IMPORTANT]
> Immediately rotate passwords in production using `/api/auth/users` or database update queries after initial deployment.

---

## 5. Maintenance & Database Backups

### Automated PostgreSQL Backup
```bash
# Dump compressed PostgreSQL database backup
docker exec -t resq_db pg_dump -U resq_user -d resq_db | gzip > resq_backup_$(date +%Y%m%d_%H%M%S).sql.gz

# Restore database from backup
gunzip -c resq_backup_YYYYMMDD_HHMMSS.sql.gz | docker exec -i resq_db psql -U resq_user -d resq_db
```

### Upgrading the Application
```bash
git pull origin main
docker compose build
docker compose up -d
```
All database tables, routes, and incidents persist in the `postgres_data` volume.
