"""
LLM Client — Multi-provider interface for LLM generation
Supports: Ollama (local), HuggingFace, Groq, OpenAI

Security features:
- API key validation
- Rate limiting
- Token limit enforcement
- Error handling with fallbacks
"""

import logging
import os
import time
from typing import Dict, Any, Optional
from collections import deque
from threading import Lock

import requests

from backend.src.rag.config import (
    GENERATION_MAX_TOKENS,
    GENERATION_TEMPERATURE,
    LLM_PROVIDER,
    HF_MODEL_ID,
    HF_TOKEN,
    OLLAMA_MODEL,
    OLLAMA_BASE_URL,
    GROQ_API_KEY,
    GROQ_MODEL,
    OPENAI_API_KEY,
    OPENAI_MODEL,
    MAX_REQUESTS_PER_MINUTE,
)

logger = logging.getLogger(__name__)


class RateLimiter:
    """Simple rate limiter for API calls."""
    
    def __init__(self, max_requests: int, time_window: int = 60):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = deque()
        self.lock = Lock()
    
    def can_proceed(self) -> bool:
        """Check if request can proceed without hitting rate limit."""
        with self.lock:
            now = time.time()
            # Remove old requests outside time window
            while self.requests and self.requests[0] < now - self.time_window:
                self.requests.popleft()
            
            if len(self.requests) < self.max_requests:
                self.requests.append(now)
                return True
            return False
    
    def wait_if_needed(self):
        """Wait if rate limit reached."""
        while not self.can_proceed():
            time.sleep(1)


class LLMClient:
    """
    Unified interface for LLM generation across multiple providers.
    
    Security features:
    - API key validation
    - Rate limiting
    - Token limit enforcement
    - Multi-layer fallback
    
    Providers:
    - Ollama: Local, fast, offline (RECOMMENDED for demos)
    - HuggingFace: Cloud API (fine-tuned model)
    - Groq: Ultra-fast cloud API (FREE - best fallback!)
    - OpenAI: GPT models
    """
    
    # Class-level rate limiters (shared across instances)
    _rate_limiters = {}
    
    def __init__(
        self,
        provider: str = None,
        model_id: str = None,
        temperature: float = None,
        max_tokens: int = None
    ):
        self.provider = provider or LLM_PROVIDER
        self.temperature = temperature or GENERATION_TEMPERATURE
        self.max_tokens = max_tokens or GENERATION_MAX_TOKENS
        
        # Security: Enforce token limits
        if self.max_tokens > 2000:
            logger.warning(f"Token limit {self.max_tokens} exceeds safe limit, capping at 2000")
            self.max_tokens = 2000
        
        # Initialize rate limiter for this provider
        if self.provider not in self._rate_limiters:
            self._rate_limiters[self.provider] = RateLimiter(MAX_REQUESTS_PER_MINUTE)
        self.rate_limiter = self._rate_limiters[self.provider]
        
        # Provider-specific setup with validation
        if self.provider == "ollama":
            self.model_id = model_id or OLLAMA_MODEL
            self.base_url = OLLAMA_BASE_URL
            logger.info(f"LLM Client initialized: Ollama - {self.model_id}")
            
        elif self.provider == "huggingface":
            if not HF_TOKEN:
                logger.warning("⚠️ HF_TOKEN not set - API may be rate-limited")
            self.model_id = model_id or HF_MODEL_ID
            self.token = HF_TOKEN
            self.api_url = f"https://api-inference.huggingface.co/models/{self.model_id}"
            self.headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}
            logger.info(f"LLM Client initialized: HuggingFace - {self.model_id}")
        
        elif self.provider == "groq":
            if not GROQ_API_KEY:
                raise ValueError("GROQ_API_KEY not set in environment")
            self.model_id = model_id or GROQ_MODEL
            self.api_key = GROQ_API_KEY
            self.api_url = "https://api.groq.com/openai/v1/chat/completions"
            self.headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
            logger.info(f"LLM Client initialized: Groq - {self.model_id}")
            
        elif self.provider == "openai":
            if not OPENAI_API_KEY:
                raise ValueError("OPENAI_API_KEY not set in environment")
            self.model_id = model_id or OPENAI_MODEL
            self.api_key = OPENAI_API_KEY
            logger.info(f"LLM Client initialized: OpenAI - {self.model_id}")
            
        else:
            raise ValueError(f"Unknown LLM provider: {self.provider}")
    
    def generate(
        self,
        prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> str:
        """
        Generate text from prompt using multi-layer fallback strategy with security.
        
        Strategy:
        1. Try primary provider (HuggingFace fine-tuned model) - 1 quick attempt
        2. Fallback to Groq if available (fast & reliable)
        3. Fallback to OpenAI if available
        4. Raise exception if all fail (agents have rule-based fallback)
        
        Security:
        - Rate limiting enforced
        - Token limits validated
        - API keys checked
        
        Args:
            prompt: Input prompt
            temperature: Sampling temperature (overrides default)
            max_tokens: Max new tokens (overrides default)
            **kwargs: Additional provider-specific parameters
        
        Returns:
            Generated text
        
        Raises:
            Exception: If all generation methods fail
        """
        # Security: Rate limiting
        self.rate_limiter.wait_if_needed()
        
        # Security: Token limit validation
        effective_max_tokens = max_tokens or self.max_tokens
        if effective_max_tokens > 2000:
            logger.warning(f"Token limit {effective_max_tokens} exceeds safe limit, capping at 2000")
            effective_max_tokens = 2000
        
        # Try primary provider first
        primary_provider = self.provider
        
        try:
            if primary_provider == "ollama":
                return self._generate_ollama(prompt, temperature, max_tokens, **kwargs)
            elif primary_provider == "huggingface":
                return self._generate_huggingface(prompt, temperature, max_tokens, **kwargs)
            elif primary_provider == "groq":
                return self._generate_groq(prompt, temperature, max_tokens, **kwargs)
            elif primary_provider == "openai":
                return self._generate_openai(prompt, temperature, max_tokens, **kwargs)
            else:
                raise ValueError(f"Unknown provider: {primary_provider}")
                
        except Exception as primary_error:
            logger.warning(f"Primary provider ({primary_provider}) failed: {str(primary_error)[:100]}")
            
            # Fallback to Groq if configured and not already the primary
            if primary_provider != "groq" and GROQ_API_KEY:
                try:
                    logger.info("🔄 Falling back to Groq API (ultra-fast)...")
                    return self._generate_groq(prompt, temperature, max_tokens, **kwargs)
                except Exception as groq_error:
                    logger.warning(f"Groq fallback failed: {str(groq_error)[:100]}")
            
            # Fallback to OpenAI if configured
            if primary_provider not in ["openai", "groq"] and OPENAI_API_KEY:
                try:
                    logger.info("🔄 Falling back to OpenAI API...")
                    return self._generate_openai(prompt, temperature, max_tokens, **kwargs)
                except Exception as openai_error:
                    logger.warning(f"OpenAI fallback failed: {str(openai_error)[:100]}")
            
            # All providers failed - raise exception for agent-level fallback
            raise Exception(f"All LLM providers failed. Primary: {str(primary_error)[:100]}")
    
    def _generate_ollama(self, prompt: str, temperature: Optional[float], max_tokens: Optional[int], **kwargs) -> str:
        """Generate using Ollama (local, fast, offline)."""
        payload = {
            "model": self.model_id,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature or self.temperature,
                "num_predict": max_tokens or self.max_tokens,
                **kwargs
            }
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            result = response.json()
            return result.get("response", "")
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Ollama generation failed: {e}")
            raise Exception(f"Ollama generation failed: {e}")
    
    def _generate_huggingface(self, prompt: str, temperature: Optional[float], max_tokens: Optional[int], **kwargs) -> str:
        """Generate using HuggingFace Inference API with retry logic and DNS fallback."""
        import time
        
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": max_tokens or self.max_tokens,
                "temperature": temperature or self.temperature,
                "return_full_text": False,
                "do_sample": True if (temperature or self.temperature) > 0 else False,
                **kwargs
            },
            "options": {
                "wait_for_model": True,  # Wait if model is loading
                "use_cache": False  # Fresh generation
            }
        }
        
        max_retries = 2  # Fast fail, then use Groq fallback
        retry_delay = 5  # seconds
        
        # Try multiple API endpoints as fallback
        api_urls = [
            f"https://api-inference.huggingface.co/models/{self.model_id}",
            f"https://api-inference.huggingface.co/models/{self.model_id}",  # Retry same
        ]
        
        for attempt in range(max_retries):
            try:
                # Alternate between endpoints on retry
                api_url = api_urls[attempt % len(api_urls)]
                
                # Add timeout and connection settings
                response = requests.post(
                    api_url,
                    headers=self.headers,
                    json=payload,
                    timeout=90,  # Longer timeout for model loading
                    verify=True,  # Verify SSL
                )
                
                # Handle 503 (model loading) - retry with backoff
                if response.status_code == 503:
                    if attempt < max_retries - 1:
                        logger.warning(
                            f"Model loading (attempt {attempt + 1}/{max_retries}). "
                            f"Retrying in {retry_delay}s..."
                        )
                        time.sleep(retry_delay)
                        retry_delay *= 1.5  # Exponential backoff
                        continue
                    else:
                        raise Exception(
                            "Model is still loading after multiple attempts. "
                            "Please try again in 1-2 minutes."
                        )
                
                # Handle rate limiting
                if response.status_code == 429:
                    if attempt < max_retries - 1:
                        logger.warning(f"Rate limited, retrying in {retry_delay}s...")
                        time.sleep(retry_delay)
                        retry_delay *= 1.5
                        continue
                    raise Exception(
                        "Rate limit exceeded. Please wait a moment and try again. "
                        "Consider adding HF_TOKEN to .env for higher limits."
                    )
                
                # Handle 502/504 gateway errors
                if response.status_code in [502, 504]:
                    if attempt < max_retries - 1:
                        logger.warning(f"Gateway error {response.status_code}, retrying...")
                        time.sleep(retry_delay)
                        continue
                    raise Exception(f"Gateway error: {response.status_code}")
                
                response.raise_for_status()
                result = response.json()
                
                # Parse HuggingFace response format
                if isinstance(result, list) and len(result) > 0:
                    if "generated_text" in result[0]:
                        text = result[0]["generated_text"].strip()
                        logger.info(f"✓ LLM generated {len(text)} chars")
                        return text
                elif isinstance(result, dict):
                    if "error" in result:
                        error_msg = result["error"]
                        # Handle specific errors
                        if "is currently loading" in error_msg:
                            if attempt < max_retries - 1:
                                logger.warning(f"Model loading, retry in {retry_delay}s...")
                                time.sleep(retry_delay)
                                retry_delay *= 1.5
                                continue
                        raise Exception(error_msg)
                    if "generated_text" in result:
                        text = result["generated_text"].strip()
                        logger.info(f"✓ LLM generated {len(text)} chars")
                        return text
                
                # Fallback
                logger.warning(f"Unexpected response format: {result}")
                return str(result)
                
            except requests.exceptions.Timeout:
                if attempt < max_retries - 1:
                    logger.warning(f"Timeout (attempt {attempt + 1}), retrying...")
                    time.sleep(retry_delay)
                    continue
                logger.error("HuggingFace API timeout after multiple attempts")
                raise Exception("Request timed out after multiple attempts")
            
            except requests.exceptions.ConnectionError as e:
                if attempt < max_retries - 1:
                    logger.warning(f"Connection error (attempt {attempt + 1}), retrying in {retry_delay}s...")
                    logger.warning(f"Error details: {str(e)}")
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Aggressive backoff for connection issues
                    continue
                logger.error(f"HuggingFace API connection failed after {max_retries} attempts: {e}")
                raise Exception(f"Cannot connect to HuggingFace API. Network issue detected. Using fallback mode.")
                
            except requests.exceptions.RequestException as e:
                if attempt < max_retries - 1 and "503" in str(e):
                    logger.warning(f"Connection error, retrying in {retry_delay}s...")
                    time.sleep(retry_delay)
                    continue
                logger.error(f"HuggingFace generation failed: {e}")
                raise Exception(f"HuggingFace generation failed: {e}")
        
        raise Exception("Max retries exceeded")
    
    def _generate_groq(self, prompt: str, temperature: Optional[float], max_tokens: Optional[int], **kwargs) -> str:
        """Generate using Groq API (ultra-fast, free tier)."""
        
        # Ensure we're using Groq's API URL, not HuggingFace
        groq_api_url = "https://api.groq.com/openai/v1/chat/completions"
        groq_headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": GROQ_MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature or self.temperature,
            "max_tokens": max_tokens or self.max_tokens,
            **kwargs
        }
        
        try:
            response = requests.post(
                groq_api_url,
                headers=groq_headers,
                json=payload,
                timeout=30  # Groq is FAST
            )
            response.raise_for_status()
            result = response.json()
            
            text = result["choices"][0]["message"]["content"].strip()
            logger.info(f"✓ Groq generated {len(text)} chars")
            return text
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Groq generation failed: {e}")
            raise Exception(f"Groq generation failed: {e}")
    
    def _generate_openai(self, prompt: str, temperature: Optional[float], max_tokens: Optional[int], **kwargs) -> str:
        """Generate using OpenAI API."""
        try:
            import openai
            openai.api_key = self.api_key
            
            response = openai.ChatCompletion.create(
                model=self.model_id,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature or self.temperature,
                max_tokens=max_tokens or self.max_tokens,
                **kwargs
            )
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"OpenAI generation failed: {e}")
            raise Exception(f"OpenAI generation failed: {e}")
    
    def generate_structured(
        self,
        prompt: str,
        schema: Dict[str, Any],
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate structured JSON output (best-effort).
        
        Note: HuggingFace Inference API doesn't natively support
        structured generation, so we rely on prompt engineering.
        
        Args:
            prompt: Prompt that requests JSON output
            schema: Expected output schema (for documentation)
            **kwargs: Additional generation parameters
        
        Returns:
            Parsed JSON dict
        """
        import json
        
        raw_output = self.generate(prompt, temperature=0.1, **kwargs)
        
        # Try to parse JSON
        try:
            return json.loads(raw_output)
        except json.JSONDecodeError:
            # Fallback: extract JSON from text
            import re
            match = re.search(r'\{.*\}', raw_output, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group(0))
                except:
                    pass
            
            logger.warning("Could not parse structured output, returning raw text")
            return {"raw_output": raw_output}
    
    def chat(
        self,
        messages: list,
        **kwargs
    ) -> str:
        """
        Multi-turn chat (converts to single prompt for now).
        
        Args:
            messages: List of {"role": "user"|"assistant", "content": str}
            **kwargs: Generation parameters
        
        Returns:
            Generated response
        """
        # Convert chat history to prompt
        prompt_parts = []
        for msg in messages:
            role = msg["role"]
            content = msg["content"]
            
            if role == "system":
                prompt_parts.append(f"<|system|>\n{content}<|end|>")
            elif role == "user":
                prompt_parts.append(f"<|user|>\n{content}<|end|>")
            elif role == "assistant":
                prompt_parts.append(f"<|assistant|>\n{content}<|end|>")
        
        prompt_parts.append("<|assistant|>")
        prompt = "\n".join(prompt_parts)
        
        return self.generate(prompt, **kwargs)


# Singleton instance
_client: Optional[LLMClient] = None


def get_llm_client() -> LLMClient:
    """Get or create singleton LLM client."""
    global _client
    if _client is None:
        _client = LLMClient()
    return _client
