# 🚀 Deployment Guide

This directory contains all deployment configurations for the Alloy Agent system.

## 📁 Files

- **`render.yaml`** - Backend deployment config for Render.com (free tier)
- **`vercel.json`** - Frontend deployment config for Vercel (free tier)
- **`Dockerfile`** - Docker container for backend service
- **`docker-compose.yml`** - Local development with Docker

---

## 🆓 Free Deployment Options

### Option 1: Render + Vercel (Recommended for Demo)

#### Backend on Render.com
1. Push code to GitHub
2. Go to [render.com](https://render.com)
3. Click "New +" → "Web Service"
4. Connect GitHub repo
5. Render will auto-detect `render.yaml`
6. Add environment variables:
   - `QDRANT_URL`
   - `QDRANT_API_KEY`
   - `HF_TOKEN`
7. Deploy (takes ~5 minutes)
8. Get URL: `https://alloy-agent-backend.onrender.com`

#### Frontend on Vercel
1. Go to [vercel.com](https://vercel.com)
2. Click "Import Project"
3. Connect GitHub repo
4. Framework Preset: Vite
5. Root Directory: `frontend`
6. Build Command: `npm run build`
7. Output Directory: `dist`
8. Add environment variable:
   - `VITE_API_URL` = `https://alloy-agent-backend.onrender.com`
9. Deploy (takes ~2 minutes)
10. Get URL: `https://alloy-agent.vercel.app`

---

### Option 2: Railway.app (Alternative)

#### Full Stack on Railway
1. Go to [railway.app](https://railway.app)
2. Click "New Project" → "Deploy from GitHub"
3. Select repo
4. Railway auto-detects Python + Node.js
5. Add environment variables
6. Deploy both services
7. Get URLs automatically

---

### Option 3: Docker (Self-Hosted)

```bash
# From project root
cd deployment
docker-compose up -d

# Access:
# Backend: http://localhost:8000
# Frontend: http://localhost:5173
```

---

## 🔧 Environment Variables Required

### Backend (.env)
```env
QDRANT_URL=https://your-cluster.qdrant.io
QDRANT_API_KEY=your_api_key
HF_MODEL_ID=CodeMasterAbdul/alloy-phi3-steel-maintenance
HF_TOKEN=hf_your_token
LLM_PROVIDER=huggingface
ENVIRONMENT=production
```

### Frontend
```env
VITE_API_URL=https://your-backend-url.com
```

---

## 📊 Free Tier Limits

| Service | Backend | Frontend | Database |
|---------|---------|----------|----------|
| **Render** | 750 hrs/month | - | - |
| **Vercel** | - | Unlimited | - |
| **Qdrant Cloud** | - | - | 1GB free |

**Total Cost: $0/month** ✅

---

## ✅ Post-Deployment Checklist

- [ ] Backend health check: `https://your-backend.com/health`
- [ ] Frontend loads correctly
- [ ] Login works (Supervisor role)
- [ ] WebSocket connects (check browser console)
- [ ] Live sensor data streams
- [ ] AI chat responds
- [ ] PDF viewer works
- [ ] Reports generate automatically
- [ ] Logbook entries create

---

## 🐛 Troubleshooting

### Backend won't start
- Check environment variables are set
- Verify `requirements.txt` installed
- Check logs: Render dashboard → Logs tab

### Frontend can't connect to backend
- Verify `VITE_API_URL` is set correctly
- Check CORS settings in backend
- Test backend directly: `curl https://your-backend.com/health`

### WebSocket not connecting
- Render free tier: WebSocket works but may sleep after 15min inactivity
- Wake up: Visit backend URL to restart

---

## 📝 Notes

- **Render free tier sleeps after 15 minutes** of inactivity. First request takes ~30s to wake up.
- **Vercel has no sleep** - frontend is always instant.
- **Database (SQLite)** persists on Render's disk (ephemeral storage - resets on redeploy).
- For **production**, use Render paid tier ($7/month) or Railway ($5/month) for persistent disk.

---

## 🔗 Useful Links

- [Render Docs](https://render.com/docs)
- [Vercel Docs](https://vercel.com/docs)
- [Railway Docs](https://docs.railway.app)
- [Docker Docs](https://docs.docker.com)
