# Alloy-Agent: Free Hosting Deployment Guide

## Live Demo for Judges - Zero Cost Setup

This guide provides a **completely free** hosting solution for your hackathon submission.

---

## Architecture Overview

```
Frontend (React + Vite) → Vercel/Netlify (Free)
    ↓
Backend API (FastAPI) → Render.com (Free)
    ↓
Vector DB (Qdrant) → Qdrant Cloud (Free 1GB)
    ↓
LLM (Fine-tuned Phi-3) → HuggingFace Inference API (Free)
```

---

## Component 1: Vector Database (Qdrant Cloud)

**Cost: FREE** (1GB cluster, no credit card required)

### Setup Steps:

1. **Create Qdrant Cloud Account**
   - Go to: https://cloud.qdrant.io/
   - Sign up with GitHub/Google
   - Create new cluster: "alloy-agent-rag"
   - Region: us-east-1 (fastest for US judges)
   - Plan: **Free 1GB** (sufficient for demo)

2. **Get Credentials**
   ```bash
   # Save these from Qdrant dashboard:
   QDRANT_URL=https://your-cluster.qdrant.io
   QDRANT_API_KEY=your-api-key-here
   ```

3. **Initialize Collections**
   ```bash
   # Run this once to create collections:
   python scripts/init_qdrant.py
   ```

---

## Component 2: Model Hosting (HuggingFace)

**Cost: FREE** (Inference API for public models)

### Your Model:
- Already uploaded: `abdul-nazeer/alloy-agent-phi3-maintenance`
- Inference API: Automatically available for public models
- Rate limit: 100 requests/day (sufficient for demo)

### API Configuration:
```python
from huggingface_hub import InferenceClient

client = InferenceClient(
    model="abdul-nazeer/alloy-agent-phi3-maintenance",
    token=os.getenv("HF_TOKEN")  # Optional, increases rate limit
)
```

**Get HF Token (free):**
1. Go to: https://huggingface.co/settings/tokens
2. Create token with "Read" access
3. Save as `HF_TOKEN` in `.env`

---

## Component 3: Backend API (Render.com)

**Cost: FREE** (750 hours/month, auto-sleep after 15min inactivity)

### Setup Steps:

1. **Prepare for Deployment**
   ```bash
   # Already done, but verify these files exist:
   - requirements.txt (optimized for deployment)
   - Dockerfile (optional, but faster)
   - render.yaml (deployment config)
   ```

2. **Create Render Account**
   - Go to: https://render.com/
   - Sign up with GitHub
   - Connect your GitHub repo: `Alloy-Agent`

3. **Deploy Backend**
   - Click "New +" → "Web Service"
   - Select your repo
   - Settings:
     ```
     Name: alloy-agent-backend
     Region: Oregon (free tier)
     Branch: main
     Build Command: pip install -r requirements.txt
     Start Command: uvicorn backend.src.api.main:app --host 0.0.0.0 --port $PORT
     Instance Type: Free
     ```

4. **Environment Variables** (in Render dashboard):
   ```bash
   QDRANT_URL=https://your-cluster.qdrant.io
   QDRANT_API_KEY=your-api-key
   HF_TOKEN=your-hf-token
   ENVIRONMENT=production
   ```

5. **Auto-Deploy**
   - Render auto-deploys on Git push
   - First deploy: ~5 minutes
   - Get URL: `https://alloy-agent-backend.onrender.com`

---

## Component 4: Frontend Dashboard (Vercel/Netlify)

**Cost: FREE** (unlimited bandwidth for personal projects)

### Technology Stack:
- **React 18** with TypeScript
- **Vite** (fast build tool)
- **TailwindCSS** (modern styling)
- **Axios** (API calls)
- **React Query** (state management)

### Setup Steps:

1. **Frontend Structure** (already in `/dashboard`):
   ```
   dashboard/
   ├── src/
   │   ├── components/
   │   │   ├── EquipmentDashboard.tsx
   │   │   ├── QueryInterface.tsx
   │   │   ├── ResultsDisplay.tsx
   │   │   └── SourceCitations.tsx
   │   ├── api/
   │   │   └── client.ts
   │   ├── App.tsx
   │   └── main.tsx
   ├── package.json
   ├── vite.config.ts
   └── index.html
   ```

2. **Deploy to Vercel** (Recommended):
   - Go to: https://vercel.com/
   - Sign in with GitHub
   - Import repository: `Alloy-Agent`
   - Settings:
     ```
     Framework: Vite
     Root Directory: dashboard
     Build Command: npm run build
     Output Directory: dist
     Install Command: npm install
     ```
   - Environment Variables:
     ```bash
     VITE_API_URL=https://alloy-agent-backend.onrender.com
     ```

3. **Alternative: Deploy to Netlify**:
   - Go to: https://netlify.com/
   - Drag & drop `dashboard/dist` folder after build
   - Or connect GitHub repo for auto-deploy

4. **Get Public URL**:
   - Vercel: `https://alloy-agent.vercel.app`
   - Netlify: `https://alloy-agent.netlify.app`
   - Share this with judges

---

## Component 5: Data Upload (One-Time Setup)

### Upload RAG Documents:

```bash
# 1. Process and upload manuals
python scripts/upload_manuals.py --collection equipment_manuals --dir data/raw/manuals

# 2. Upload maintenance logs (training data)
python scripts/upload_logs.py --collection historical_logs --file data/training/train.jsonl

# 3. Upload SOPs
python scripts/upload_sops.py --collection maintenance_sops --dir data/raw/sops
```

### Verify Upload:
```bash
# Check collection stats
python scripts/check_qdrant.py
```

Expected output:
```
✓ equipment_manuals: 234 documents
✓ maintenance_sops: 45 documents  
✓ historical_logs: 1,776 documents
✓ fault_patterns: 0 documents (optional)
```

---

## Alternative: All-in-One Backend Deploy

If you want to keep it simple, deploy everything from backend:

### Single Render Service:

```yaml
# render.yaml
services:
  - type: web
    name: alloy-agent-api
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn backend.src.api.main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: QDRANT_URL
        sync: false
      - key: QDRANT_API_KEY
        sync: false
      - key: HF_TOKEN
        sync: false
```

---

## Cost Breakdown (Monthly)

| Service | Plan | Cost |
|---------|------|------|
| Qdrant Cloud | Free 1GB | $0 |
| HuggingFace Inference | Free Tier | $0 |
| Render Backend | Free 750h | $0 |
| Vercel/Netlify Frontend | Free | $0 |
| **TOTAL** | | **$0/month** |

**Notes:**
- Free tier limitations: 
  - Render: Apps sleep after 15min inactivity (30s cold start)
  - HF: 100 API calls/day (enough for demo)
  - Qdrant: 1GB storage (~10k documents)
  - Vercel/Netlify: Unlimited bandwidth, instant CDN
- Perfect for hackathon judging period
- React frontend much more professional than Streamlit
- Can upgrade later if needed

---

## Deployment Checklist

### Before Deploying:

- [ ] Create Qdrant Cloud cluster
- [ ] Get Qdrant URL and API key
- [ ] Create HuggingFace token
- [ ] Push code to GitHub
- [ ] Create `.env.production` file with all keys
- [ ] Test locally with production config

### Deploy Backend:

- [ ] Create Render account
- [ ] Connect GitHub repo
- [ ] Create backend web service
- [ ] Add environment variables
- [ ] Wait for first deploy (~5 min)
- [ ] Test API endpoint: `/health`

### Deploy Frontend:

- [ ] Build React app locally
- [ ] Deploy to Vercel (recommended) or Netlify
- [ ] Add backend URL to env vars
- [ ] Test dashboard access
- [ ] Verify responsive design

### Upload Data:

- [ ] Run upload scripts for each collection
- [ ] Verify data in Qdrant dashboard
- [ ] Test RAG search functionality

### Final Testing:

- [ ] Test full query flow: Frontend → Backend → Qdrant → HF
- [ ] Verify response time (<5 seconds)
- [ ] Test on different devices
- [ ] Share demo URL with team

---

## Troubleshooting

### Backend Won't Start:
```bash
# Check logs in Render dashboard
# Common issues:
- Missing environment variables
- Wrong Python version (use 3.11)
- Dependency conflicts (rebuild with fresh requirements)
```

### Qdrant Connection Failed:
```bash
# Verify URL format (must include https://)
# Check API key is correct
# Test connection locally:
python -c "from qdrant_client import QdrantClient; print(QdrantClient(url='YOUR_URL', api_key='YOUR_KEY').get_collections())"
```

### HuggingFace Rate Limit:
```bash
# Add HF_TOKEN to increase limit
# Or: Implement response caching in backend
# Or: Use smaller model as fallback
```

### Cold Start Delays:
```bash
# Free tier sleeps after 15min
# First request takes 30-60s
# Solution: Keep-alive ping every 10min (optional)
```

---

## Post-Hackathon Upgrade Path

If judges love it and you need production:

### Recommended Upgrades:
1. **Render**: $7/month → Always-on, faster instances
2. **Qdrant**: $25/month → 4GB cluster, better performance
3. **HuggingFace**: $9/month → Inference endpoints (guaranteed uptime)

**Total**: ~$41/month for production-ready system

---

## Demo Script for Judges

When presenting:

1. **Show Live Dashboard**: 
   - "This is running 100% on free cloud infrastructure"

2. **Demo Query**:
   - Input: "Air compressor temperature 95°C, vibration 1.2mm/s"
   - Show: RAG retrieval → Relevant manual sections → LLM analysis

3. **Highlight Features**:
   - Real-time equipment diagnostics
   - Document-grounded responses (show sources)
   - Fine-tuned model (reference training achievements)

4. **Technical Stack**:
   - "Vector DB on Qdrant Cloud, fine-tuned Phi-3 on HuggingFace, hosted on Render"
   - "Zero hosting cost, production-ready architecture"

---

## Support & Monitoring

### Health Checks:
- Backend: `https://alloy-agent-backend.onrender.com/health`
- Frontend: Dashboard home page load time
- Qdrant: Cloud dashboard shows uptime

### Logs:
- Render: View logs in dashboard
- Qdrant: Query history in cloud console
- HuggingFace: Inference API usage stats

### Uptime:
- Free tier: 99%+ uptime
- Cold starts: 30-60s after 15min idle
- Active time: <1s response

---

## Security Notes

### Publicly Accessible:
- Demo is public (no authentication)
- Don't expose sensitive data
- Use placeholder equipment IDs for demo

### API Keys:
- Store in Render environment variables (secure)
- Never commit to Git
- Rotate after hackathon if needed

### Rate Limiting:
- Implement simple rate limits in backend
- Prevent abuse during judging

---

## Backup Plan

If Render has issues:

### Alternative Hosts (also free):
1. **Railway.app**: Similar to Render, $5 free credit
2. **Fly.io**: 3 small VMs free
3. **Vercel**: Serverless functions (for API)
4. **Streamlit Cloud**: All-in-one (easiest)

### Recommended: Have Streamlit Cloud ready as backup

---

## Questions for Judges?

**Common Questions:**

Q: "Is this really free?"  
A: "Yes, using free tiers of enterprise-grade tools. Total cost: $0/month"

Q: "Can it scale?"  
A: "Architecture is production-ready. Upgrade to paid tiers handles 10k+ users"

Q: "Where's the model?"  
A: "Fine-tuned Phi-3 on HuggingFace: abdul-nazeer/alloy-agent-phi3-maintenance"

Q: "How accurate is RAG?"  
A: "Retrieves from 2k+ maintenance records with 0.025 eval loss model"

---

## Next Steps

1. Follow setup steps above
2. Test everything locally first
3. Deploy to Render
4. Upload data to Qdrant
5. Test end-to-end
6. Share demo URL in submission

**Estimated Setup Time**: 2-3 hours

**Demo Will Be Live At**:
- Frontend: `https://alloy-agent.vercel.app` (React UI)
- API: `https://alloy-agent-backend.onrender.com`
- API Docs: `https://alloy-agent-backend.onrender.com/docs`
- Tech Stack: **React + FastAPI + Qdrant + HuggingFace** (all CPU-only, no GPU)

Good luck with the hackathon! 🚀
