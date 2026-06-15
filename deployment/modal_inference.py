"""
Modal.com deployment for alloy-phi3-steel-maintenance model
Free tier: $30/month credits - perfect for hackathon demos

Setup:
1. Install: pip install modal
2. Login: modal token new
3. Deploy: modal deploy modal_inference.py
4. Get URL and update .env with MODAL_ENDPOINT_URL
"""

import modal

# Create Modal app
app = modal.App("alloy-phi3-inference")

# Define container image with required dependencies
image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install(
        "transformers>=4.35.0",
        "torch>=2.1.0",
        "accelerate>=0.25.0",
        "sentencepiece>=0.1.99",
        "protobuf>=3.20.0",
    )
)

# Model configuration
MODEL_ID = "CodeMasterAbdul/alloy-phi3-steel-maintenance"
MODEL_REVISION = "main"


@app.cls(
    image=image,
    gpu="T4",  # Free tier GPU
    timeout=300,
    container_idle_timeout=60,
    allow_concurrent_inputs=10,
)
class Model:
    """
    Phi-3 Mini fine-tuned for steel maintenance diagnostics.
    
    Loads model on container startup and keeps it in memory.
    Subsequent requests are fast (~1-2 seconds).
    """
    
    @modal.build()
    def download_model(self):
        """Download model at build time to speed up cold starts."""
        from transformers import AutoModelForCausalLM, AutoTokenizer
        
        print(f"Downloading {MODEL_ID}...")
        AutoTokenizer.from_pretrained(MODEL_ID, revision=MODEL_REVISION)
        AutoModelForCausalLM.from_pretrained(
            MODEL_ID,
            revision=MODEL_REVISION,
            torch_dtype="auto",
            trust_remote_code=True,
        )
        print("Model downloaded successfully!")
    
    @modal.enter()
    def load_model(self):
        """Load model into GPU memory on container start."""
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer
        
        print("Loading model into GPU memory...")
        
        self.tokenizer = AutoTokenizer.from_pretrained(
            MODEL_ID,
            revision=MODEL_REVISION,
        )
        
        self.model = AutoModelForCausalLM.from_pretrained(
            MODEL_ID,
            revision=MODEL_REVISION,
            torch_dtype=torch.float16,
            device_map="auto",
            trust_remote_code=True,
        )
        
        self.model.eval()
        print("Model loaded and ready!")
    
    @modal.method()
    def generate(
        self,
        prompt: str,
        max_new_tokens: int = 800,
        temperature: float = 0.3,
        top_p: float = 0.9,
        do_sample: bool = True,
    ) -> dict:
        """
        Generate text from prompt.
        
        Args:
            prompt: Input text
            max_new_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0.0 = deterministic)
            top_p: Nucleus sampling parameter
            do_sample: Whether to use sampling
        
        Returns:
            dict with 'generated_text' and metadata
        """
        import torch
        import time
        
        start_time = time.time()
        
        # Tokenize
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
        
        # Generate
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                temperature=temperature,
                top_p=top_p,
                do_sample=do_sample,
                pad_token_id=self.tokenizer.eos_token_id,
            )
        
        # Decode
        generated_text = self.tokenizer.decode(
            outputs[0][inputs.input_ids.shape[1]:],  # Skip input prompt
            skip_special_tokens=True,
        )
        
        generation_time = time.time() - start_time
        
        return {
            "generated_text": generated_text.strip(),
            "metadata": {
                "model": MODEL_ID,
                "prompt_tokens": inputs.input_ids.shape[1],
                "generated_tokens": outputs.shape[1] - inputs.input_ids.shape[1],
                "generation_time_seconds": round(generation_time, 2),
                "parameters": {
                    "temperature": temperature,
                    "top_p": top_p,
                    "max_new_tokens": max_new_tokens,
                }
            }
        }


# ══════════════════════════════════════════════════════════════════════════════
# Web endpoint for HTTP API
# ══════════════════════════════════════════════════════════════════════════════

@app.function(image=image)
@modal.web_endpoint(method="POST")
def api_generate(request: dict) -> dict:
    """
    HTTP API endpoint compatible with HuggingFace Inference API format.
    
    POST /api_generate
    {
        "inputs": "prompt text",
        "parameters": {
            "max_new_tokens": 800,
            "temperature": 0.3,
            "top_p": 0.9,
            "do_sample": true
        }
    }
    
    Returns:
    [
        {
            "generated_text": "...",
        }
    ]
    """
    prompt = request.get("inputs", "")
    if not prompt:
        return {"error": "Missing 'inputs' field"}
    
    params = request.get("parameters", {})
    
    # Call model
    model = Model()
    result = model.generate.remote(
        prompt=prompt,
        max_new_tokens=params.get("max_new_tokens", 800),
        temperature=params.get("temperature", 0.3),
        top_p=params.get("top_p", 0.9),
        do_sample=params.get("do_sample", True),
    )
    
    # Return in HuggingFace format
    return [{"generated_text": result["generated_text"]}]


# ══════════════════════════════════════════════════════════════════════════════
# CLI for local testing
# ══════════════════════════════════════════════════════════════════════════════

@app.local_entrypoint()
def main(prompt: str = "Diagnose high temperature in air compressor"):
    """Test the model locally."""
    print(f"\n{'='*60}")
    print(f"Testing model with prompt:")
    print(f"{prompt}")
    print(f"{'='*60}\n")
    
    model = Model()
    result = model.generate.remote(prompt)
    
    print(f"Generated text:\n{result['generated_text']}")
    print(f"\nMetadata:")
    for key, value in result['metadata'].items():
        print(f"  {key}: {value}")
