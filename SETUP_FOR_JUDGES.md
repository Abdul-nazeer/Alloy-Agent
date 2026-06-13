# 🎯 Setup Guide for Hackathon Judges

**Quick setup to run and evaluate the Alloy-Agent system**

## ⚡ Quick Start (5 minutes)

### Option 1: View Pre-trained Model & Results

If you want to skip training and see results immediately:

```bash
# 1. Extract submission
unzip Alloy-Agent.zip
cd Alloy-Agent

# 2. Install dependencies
pip install -r requirements.txt

# 3. View training results
# Open: models/training_results/wandb_report.html
# Or visit: https://wandb.ai/[our-project-link]

# 4. Test the fine-tuned model
python models/test_inference.py
```

### Option 2: Full Training Pipeline

To reproduce training from scratch:

```bash
# 1. Setup environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
pip install -r models/requirements-training.txt

# 2. Data is already processed
ls data/training/  # train.jsonl, val.jsonl ready

# 3. Setup WandB (optional but recommended)
wandb login  # Enter API key from https://wandb.ai/authorize

# 4. Start training
cd models
jupyter notebook train_model.ipynb
# Or: python -m jupyter notebook train_model.ipynb

# Training time: ~2-3 hours on T4 GPU (Google Colab free tier works!)
```

## 📊 What to Look For

### 1. Data Quality (10 points)
- **Location**: `data/training/validation_report.txt`
- **Check**: 100% success rate, 1,973 samples, proper distribution
- **Evidence**: No errors, clean metadata, balanced severity levels

### 2. Code Quality (15 points)
```bash
# Run code quality checks
pip install -r requirements-dev.txt
pre-commit run --all-files

# Code metrics
flake8 --statistics data/scripts/
pylint data/scripts/ --rcfile=.pylintrc
```
- **Location**: `.pre-commit-config.yaml`, `pyproject.toml`
- **Check**: Black formatted, type hints, docstrings, no linting errors

### 3. Fine-tuning Setup (25 points)
- **Location**: `models/train_model.ipynb`
- **Check**: 
  - LoRA rank 32 (optimized for domain)
  - All attention + FFN layers targeted
  - Proper quantization (4-bit NF4)
  - WandB integration
  - SFTTrainer from TRL

### 4. Model Card & Documentation (10 points)
- **Location**: `models/MODEL_CARD.md`
- **Check**: 
  - Training config documented
  - Usage examples
  - Limitations clearly stated
  - Ethical considerations

### 5. Production Readiness (15 points)
```bash
# Check structure
tree -L 2

# Check git history
git log --oneline --graph

# Check CI/CD
cat .github/workflows/*.yml  # (if present)
```
- **Evidence**: 
  - Clean branching strategy
  - Focused commits
  - Pre-commit hooks
  - Docker-ready
  - Proper .gitignore

## 🎬 Running the Demo

### Test Inference

```python
# Quick test
cd models
python << 'EOF'
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel

# Load model (adjust path if needed)
base_model = AutoModelForCausalLM.from_pretrained(
    "microsoft/Phi-3-mini-4k-instruct",
    device_map="auto",
    trust_remote_code=True
)
model = PeftModel.from_pretrained(base_model, "./phi3-steel-maintenance/final")
tokenizer = AutoTokenizer.from_pretrained("./phi3-steel-maintenance/final")

# Test
prompt = """<|system|>
You are an expert AI for steel plant maintenance.<|end|>
<|user|>
Equipment: Air Compressor | Temperature: 115°C | Vibration: 95 Hz
Status: High temperature alarm<|end|>
<|assistant|>
"""

inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
outputs = model.generate(**inputs, max_new_tokens=300)
print(tokenizer.decode(outputs[0], skip_special_tokens=True))
EOF
```

## 📈 Evaluation Metrics

### Where to Find Results

1. **WandB Dashboard**: 
   - URL: [Insert your WandB project link]
   - Metrics: Loss curves, learning rate, validation metrics
   - Compare: Base vs Fine-tuned

2. **Local Logs**:
   ```bash
   cat models/phi3-steel-maintenance/trainer_state.json
   cat models/phi3-steel-maintenance/training_args.bin
   ```

3. **Model Performance**:
   ```bash
   # Check final metrics
   ls models/phi3-steel-maintenance/checkpoint-*/
   ```

## 🔍 Key Differentiators

### What Makes This Submission Stand Out:

1. **Actually Fine-Tuned** ✅
   - Not just mentioned - fully implemented
   - Training notebook with all cells executed
   - WandB tracking for transparency

2. **Production-Grade Data Pipeline** ✅
   - 3 data processors (UCI, CMAPSS, Synthetic)
   - Validation with 100% success rate
   - Comprehensive error handling

3. **Optimized Hyperparameters** ✅
   - Research-backed LoRA configuration
   - Rank 32 for complex domain
   - Alpha = 2×rank for stability
   - All attention + FFN layers

4. **Professional Code Quality** ✅
   - Pre-commit hooks
   - Black + isort + flake8
   - Type hints and docstrings
   - Clean git history

5. **Complete Documentation** ✅
   - Model card with limitations
   - Contributing guidelines
   - Setup instructions
   - Ethical considerations

## 🛠️ Troubleshooting

### Common Issues:

**1. CUDA Out of Memory**
```bash
# Reduce batch size in notebook
BATCH_SIZE = 2  # instead of 4
GRAD_ACCUM = 4  # instead of 2
```

**2. WandB Not Logging**
```bash
# Re-login
wandb login --relogin
```

**3. Model Not Loading**
```bash
# Check path
ls models/phi3-steel-maintenance/final/
# Should contain: adapter_config.json, adapter_model.bin
```

## 📞 Contact

For questions during evaluation:
- **GitHub Issues**: [repo-url]/issues
- **Documentation**: See `docs/` folder
- **Model Card**: `models/MODEL_CARD.md`

## ⏱️ Estimated Review Time

- **Quick Review** (code quality, structure): 10 minutes
- **Data Inspection** (validation report): 5 minutes
- **Training Review** (notebook walkthrough): 15 minutes
- **Testing** (run inference): 10 minutes

**Total**: ~40 minutes for comprehensive evaluation

---

## 🎯 Scoring Checklist

- [ ] Data processing pipeline functional
- [ ] Training notebook complete
- [ ] Model weights present
- [ ] WandB tracking configured
- [ ] Code quality checks pass
- [ ] Documentation complete
- [ ] Inference works
- [ ] Professional structure

---

Thank you for evaluating Alloy-Agent! 🙏
