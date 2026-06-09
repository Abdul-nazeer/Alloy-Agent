# Phi-3 Steel Plant Maintenance Model

## Model Description

Fine-tuned Microsoft Phi-3-mini-4k-instruct for predictive maintenance in steel manufacturing plants using QLoRA.

**Base Model**: microsoft/Phi-3-mini-4k-instruct  
**Method**: QLoRA (4-bit quantization + LoRA adapters)  
**Domain**: Industrial Predictive Maintenance  
**Use Case**: Steel plant equipment diagnostics and maintenance planning

## Training Data

- **Total Samples**: 1,973 (1,776 train / 197 validation)
- **Sources**:
  - UCI AI4I Manufacturing: 355 samples
  - NASA CMAPSS Turbofan: 1,418 samples
  - Synthetic Edge Cases: 200 samples

- **Equipment Types**: Air Compressors, Cooling Fans, Rolling Mills, Conveyors
- **Failure Modes**: 7 fault types across multiple severity levels
- **RUL Range**: 1 hour to 800+ hours

## Training Configuration

### LoRA Parameters
- **Rank (r)**: 32
- **Alpha**: 64
- **Dropout**: 0.1
- **Target Modules**: q_proj, k_proj, v_proj, o_proj, gate_proj, up_proj, down_proj

### Training Hyperparameters
- **Epochs**: 3
- **Batch Size**: 4 (effective: 8 with gradient accumulation)
- **Learning Rate**: 2e-4
- **LR Scheduler**: Cosine with 100 warmup steps
- **Optimizer**: Paged AdamW 32-bit
- **Precision**: BF16
- **Max Sequence Length**: 2048 tokens

### Optimization
- 4-bit NF4 quantization
- Double quantization
- Gradient checkpointing
- Flash Attention 2
- Gradient clipping (max_norm=1.0)
- Weight decay: 0.01

## Performance

### Experiment Tracking

**Dual tracking for transparency and reproducibility:**

1. **WandB** (Primary): [Link to WandB run]
   - Real-time loss curves
   - Hyperparameter logging
   - Model versioning
   - Team collaboration

2. **TensorBoard** (Local): `tensorboard --logdir=./phi3-steel-maintenance/logs`
   - Training/validation loss
   - Learning rate schedule
   - Gradient norms
   - System metrics (GPU, CPU, memory)

**Metrics** (to be filled after training):
- Final Training Loss: TBD
- Final Validation Loss: TBD  
- Training Time: TBD
- GPU Memory Peak: TBD
- Throughput: TBD samples/sec

## Usage

### Loading the Model

```python
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel
import torch

# Load base model
base_model = AutoModelForCausalLM.from_pretrained(
    "microsoft/Phi-3-mini-4k-instruct",
    device_map="auto",
    trust_remote_code=True,
    torch_dtype=torch.bfloat16
)

# Load LoRA adapter
model = PeftModel.from_pretrained(base_model, "./phi3-steel-maintenance/final")
tokenizer = AutoTokenizer.from_pretrained("./phi3-steel-maintenance/final")

print("Model loaded successfully!")
```

### Inference Example

```python
# Format prompt in Phi-3 chat template
prompt = """<|system|>
You are an expert AI system for predictive maintenance in steel manufacturing plants.<|end|>
<|user|>
Equipment: Air Compressor Unit | ID: AC-101
Operating Hours: 12,450 hours

Current Sensor Readings:
- Discharge Temperature: 118°C (baseline: 85°C)
- Discharge Pressure: 7.2 bar (baseline: 8.5 bar)
- Vibration Level: 105 Hz (baseline: 80 Hz)
- Operating Efficiency: 87% (baseline: 100%)

Alert: Multiple parameter deviations detected<|end|>
<|assistant|>
"""

inputs = tokenizer(prompt, return_tensors="pt").to(model.device)

with torch.no_grad():
    outputs = model.generate(
        **inputs,
        max_new_tokens=600,
        temperature=0.7,
        do_sample=True,
        top_p=0.9,
        repetition_penalty=1.1
    )

response = tokenizer.decode(outputs[0], skip_special_tokens=True)
print(response)
```

### Hugging Face Hub (Optional)

```python
# Push to Hub for easy sharing/demo
model.push_to_hub("your-username/phi3-steel-maintenance")
tokenizer.push_to_hub("your-username/phi3-steel-maintenance")

# Load from Hub
from peft import PeftModel
model = PeftModel.from_pretrained(
    "microsoft/Phi-3-mini-4k-instruct",
    "your-username/phi3-steel-maintenance"
)
```

## Capabilities

The model can:
- ✅ Analyze sensor data from industrial equipment
- ✅ Diagnose equipment failures and degradation
- ✅ Predict remaining useful life (RUL)
- ✅ Provide root cause analysis
- ✅ Generate maintenance recommendations
- ✅ Estimate downtime and spare parts needed
- ✅ Suggest long-term preventive measures

## Limitations

- Trained specifically for steel plant equipment
- Limited to equipment types in training data
- Requires properly formatted sensor inputs
- Not validated on real production systems
- Recommendations should be reviewed by qualified engineers

## Ethical Considerations

- **Safety Critical**: This model's outputs should NOT be the sole basis for maintenance decisions
- **Human Oversight**: All recommendations must be reviewed by qualified maintenance engineers
- **Liability**: Model is for assistance only, not autonomous decision-making
- **Data Privacy**: Ensure no sensitive plant data is exposed in production use

## Citation

```bibtex
@misc{alloy-agent-2026,
  title={Phi-3 Steel Plant Maintenance Agent},
  author={Alloy-Agent Team},
  year={2026},
  howpublished={Hackathon Submission}
}
```

## License

Model weights inherit license from base Phi-3 model (MIT License).  
Training code and data processing pipeline: MIT License.

## Contact

For questions or issues: [Repository Issues](https://github.com/Abdul-nazeer/Alloy-Agent/issues)
