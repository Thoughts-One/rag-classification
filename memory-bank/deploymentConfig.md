## Render.com Deployment Configuration (rag-classification)

### General Settings
- **Service Name:** `rag-classification`
- **Region:** `Frankfurt (EU Central)`
- **Instance Type:** `Free (0.1 CPU, 512 MB)`

### Build & Deploy
- **Repository:** `https://github.com/Thoughts-One/rag-classification`
- **Branch:** `main`
- **Git Credentials User:** `kai.fickenscher+ptreclassification@gmail.com`
- **Root Directory:** (Not set)
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `gunicorn --worker-class uvicorn.workers.UvicornWorker app:application`
- **Auto-Deploy:** `On Commit`
- **Deploy Hook:** (Configured, sensitive value not stored)

### Custom Domains
- **Render Subdomain:** `https://rag-classification.onrender.com`

### Health Checks
- **Health Check Path:** `/api/v1/health`

### Other Settings
- **PR Previews:** `Off`
- **Service Notifications:** `Use workspace default (Only failure notifications)`
- **Preview Environment Notifications:** `Use account default (Disabled)`
- **Maintenance Mode:** `Maintenance Mode Disabled`

[2025-06-26 10:16:55] - Added initial deployment configuration