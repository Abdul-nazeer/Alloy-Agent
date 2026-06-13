---
language:
- en
license: apache-2.0
tags:
- phi-3
- qlora
- predictive-maintenance
- industrial-ai
- steel-manufacturing
library_name: transformers
pipeline_tag: text-generation
base_model: microsoft/Phi-3-mini-4k-instruct
model-index:
- name: alloy-agent-phi3-maintenance
  results:
  - task:
      type: text-generation
    metrics:
    - name: Evaluation Loss
      type: loss
      value: 0.02508
---

<div align="center">

# Alloy-Agent Phi-3 Maintenance

### Industrial Predictive Maintenance Model

Fine-tuned Phi-3-mini-4k-instruct for equipment diagnostics and maintenance planning in steel manufacturing plants

---

[![Model](https://img.shields.io/badge/Model-Phi--3--Mini-blue.svg)](https://huggingface.co/microsoft/Phi-3-mini-4k-instruct)
[![Method](https://img.shields.io/badge/Method-QLoRA-orange.svg)]()
[![Eval Loss](https://img.shields.io/badge/Eval_Loss-0.02508-brightgreen.svg)]()
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)

[Model Card](#model-overview) • [Usage](#usage) • [Training](#training-configuration) • [Performance](#performance) • [Citation](#citation)

---

</div>

## Model Overview

QLoRA fine-tuned version of microsoft/Phi-3-mini-4k-instruct (3.8B parameters) specialized for equipment maintenance analysis in industrial settings.

**Capabilities:**
- Equipment failure diagnosis from sensor data
- Remaining useful life (RUL) prediction
- Root cause analysis
- Risk level classification (LOW/MEDIUM/HIGH/CRITICAL)
- Maintenance procedure generation

**Training Data:** 1,973 maintenance records from NASA CMAPSS turbofan data, UCI AI4I 2020 dataset, and synthetic industrial scenarios.

**Performance:** Achieved 0.02508 evaluation loss after 4.5 hours of training on T4 GPU.

---

## Training Data

Dataset: 1,973 maintenance records combining NASA CMAPSS turbofan data, UCI AI4I 2020 predictive maintenance dataset, and synthetic domain scenarios.

Split: 1,776 training / 197 validation

Input format:
```
Equipment: [type] | ID: [id]
Operating Hours: [hours]
Sensor Readings: Temperature, Vibration, Pressure, etc.
```

Output format:
```
DIAGNOSIS: [failure analysis]
ROOT CAUSE: [technical cause]
RISK LEVEL: [LOW/MEDIUM/HIGH/CRITICAL]
RUL: [hours] ± [confidence]
RECOMMENDATIONS: [maintenance actions]
```

---

## Training Configuration

Hardware: Google Colab T4 GPU (15GB VRAM)  
Duration: 4.5 hours, 666 steps over 3 epochs  
Final eval loss: **0.02508**

Method: QLoRA (4-bit quantization + LoRA adapters)
- LoRA rank: 16, alpha: 16, dropout: 0.05
- Target modules: all attention and MLP projection layers
- Trainable params: 29.9M / 3.8B (0.78%)

Hyperparameters:
```
learning_rate: 2e-4
batch_size: 8 (2 per device, 4 gradient accumulation steps)
optimizer: adamw_8bit
weight_decay: 0.01
warmup_steps: 50
max_grad_norm: 1.0
lr_scheduler: linear
fp16: True
gradient_checkpointing: True
```

Training utilized Unsloth for 2x speedup during fine-tuning.

---

## Usage

Basic inference:

```python
from transformers import AutoModelForCausalLM, AutoTokenizer

model = AutoModelForCausalLM.from_pretrained(
    "abdul-nazeer/alloy-agent-phi3-maintenance",
    device_map="auto",
    torch_dtype="auto",
    trust_remote_code=True
)
tokenizer = AutoTokenizer.from_pretrained("abdul-nazeer/alloy-agent-phi3-maintenance")

prompt = """<|system|>You are an industrial maintenance AI assistant specialized in steel plant equipment analysis.<|end|>
<|user|>Equipment: Air Compressor Unit
Temperature: 95°C (baseline: 75°C)
Vibration: 1.2 mm/s (baseline: 0.5 mm/s)
Pressure: 7.8 bar (baseline: 8.5 bar)
Operating Hours: 2,150 hours

Analyze and provide maintenance recommendations.<|end|>
<|assistant|>"""

inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
outputs = model.generate(
    **inputs,
    max_new_tokens=400,
    temperature=0.7,
    do_sample=True,
    top_p=0.9
)
response = tokenizer.decode(outputs[0], skip_special_tokens=True)
print(response.split("<|assistant|>")[1])
```

For faster inference with 4-bit quantization:

```python
from unsloth import FastLanguageModel

model, tokenizer = FastLanguageModel.from_pretrained(
    model_name="abdul-nazeer/alloy-agent-phi3-maintenance",
    max_seq_length=4096,
    dtype=None,
    load_in_4bit=True,
)
FastLanguageModel.for_inference(model)
```

---

## Performance

Training converged smoothly with no overfitting:

```
Step   0: train_loss ~2.50
Step 100: train_loss 0.52, eval_loss 0.0687
Step 200: train_loss 0.18
Step 400: train_loss 0.08
Step 666: train_loss 0.025, eval_loss 0.02508
```

Loss reduction: 2.5 → 0.025 (100x improvement)

Inference: ~0.7s per response on T4 GPU with 4-bit quantization

---

## Limitations

- Trained primarily on steel plant equipment data - performance on other industrial domains may vary
- Outputs should be validated by maintenance engineers for critical systems
- Model provides estimates, not guarantees - RUL predictions have inherent uncertainty
- English language only
- Requires structured sensor data inputs for best results

## Use Cases

The model is designed for decision support in industrial maintenance:
- Early failure detection from sensor anomalies
- RUL estimation for maintenance scheduling
- Root cause analysis during equipment diagnostics
- Generating maintenance work orders and procedures

Not intended for:
- Autonomous control of equipment
- Safety-critical decisions without human review
- Financial/legal advice
- Medical equipment diagnostics

---

## Technical Details

Architecture: Phi-3-mini-4k-instruct base
- Total parameters: 3.82B
- Trainable (LoRA): 29.88M (0.78%)
- Quantization: 4-bit NF4
- Context window: 4096 tokens (2048 used in training)
- Attention heads: 32
- Hidden size: 3072
- Layers: 32

Requirements:
- Minimum: 4GB GPU VRAM (with 4-bit quantization)
- Recommended: 8GB+ GPU VRAM for production
- Dependencies: transformers, torch, accelerate, bitsandbytes

---

## Citation

If you use this model, please reference:

```bibtex
@software{alloy_agent_phi3,
  author = {Abdul Nazeer},
  title = {Alloy-Agent Phi-3: Fine-Tuned Model for Industrial Predictive Maintenance},
  year = {2024},
  url = {https://huggingface.co/abdul-nazeer/alloy-agent-phi3-maintenance}
}
```

Base model: [microsoft/Phi-3-mini-4k-instruct](https://huggingface.co/microsoft/Phi-3-mini-4k-instruct)

---

## License

Apache 2.0 (inherited from Phi-3 base model)

## Acknowledgments

Built on microsoft/Phi-3-mini-4k-instruct. Training optimized with Unsloth. Datasets sourced from NASA CMAPSS and UCI AI4I 2020.

---

<div align="center">

**Developed for Industrial AI Applications**

[GitHub Repository](https://github.com/abdul-nazeer/Alloy-Agent) • [Report Issues](https://github.com/abdul-nazeer/Alloy-Agent/issues)

</div>
