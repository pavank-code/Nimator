from typing import Dict, List, Optional, Tuple
import json
import httpx
import asyncio
import random
from app.config import settings


class LLMClient:
    """Multi-provider LLM client supporting Groq, OpenRouter, Gemini, and OpenAI."""
    
    PROVIDERS = {
        "groq": {
            "url": "https://api.groq.com/openai/v1/chat/completions",
            "key_setting": "GROQ_API_KEY",
            "model_setting": "GROQ_MODEL",
            "format": "openai"
        },
        "openrouter": {
            "url": "https://openrouter.ai/api/v1/chat/completions",
            "key_setting": "OPENROUTER_API_KEY",
            "model_setting": "OPENROUTER_MODEL",
            "format": "openai"
        },
        "openai": {
            "url": "https://api.openai.com/v1/chat/completions",
            "key_setting": "OPENAI_API_KEY",
            "model_setting": "OPENAI_MODEL",
            "format": "openai"
        },
        "gemini": {
            "url": "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
            "key_setting": "GEMINI_API_KEY",
            "model_setting": "GEMINI_MODEL",
            "format": "gemini"
        }
    }
    
    def __init__(self):
        self.provider, self.api_key, self.model = self._detect_provider()
        # Build fallback providers list
        self.fallback_providers = self._get_fallback_providers()
    
    def _get_fallback_providers(self) -> List[Tuple[str, str, str]]:
        """Get list of available fallback providers."""
        fallbacks = []
        priority = ["groq", "openrouter", "openai", "gemini"]
        for provider in priority:
            if provider == self.provider:
                continue  # Skip primary provider
            key_attr = self.PROVIDERS[provider]["key_setting"]
            model_attr = self.PROVIDERS[provider]["model_setting"]
            key = getattr(settings, key_attr, None)
            if key:
                model = getattr(settings, model_attr, None)
                fallbacks.append((provider, key, model))
        return fallbacks
    
    def _detect_provider(self) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """Auto-detect which provider to use based on available API keys."""
        if settings.LLM_PROVIDER != "auto":
            # Use explicitly set provider
            provider = settings.LLM_PROVIDER
            if provider in self.PROVIDERS:
                key = getattr(settings, self.PROVIDERS[provider]["key_setting"], None)
                model = getattr(settings, self.PROVIDERS[provider]["model_setting"], None)
                if key:
                    return provider, key, model
        
        # Auto-detect: try each provider in priority order
        # Gemini is now prioritized for two-stage pipeline
        priority = ["gemini", "groq", "openrouter", "openai"]
        for provider in priority:
            key_attr = self.PROVIDERS[provider]["key_setting"]
            model_attr = self.PROVIDERS[provider]["model_setting"]
            key = getattr(settings, key_attr, None)
            if key:
                model = getattr(settings, model_attr, None)
                print(f"Using LLM provider: {provider}")
                return provider, key, model
        
        return None, None, None
    
    async def chat(self, prompt: str, temperature: float = 0.1, max_tokens: int = 200) -> Optional[str]:
        """Send a chat request to the detected LLM provider with retry logic and fallbacks."""
        # Try primary provider first
        result = await self._try_provider(
            self.provider, self.api_key, self.model, 
            prompt, temperature, max_tokens
        )
        if result:
            return result
        
        # Try fallback providers
        for fb_provider, fb_key, fb_model in self.fallback_providers:
            print(f"Falling back to provider: {fb_provider}")
            result = await self._try_provider(
                fb_provider, fb_key, fb_model,
                prompt, temperature, max_tokens
            )
            if result:
                return result
        
        return None
    
    async def _try_provider(
        self, provider: str, api_key: str, model: str,
        prompt: str, temperature: float, max_tokens: int
    ) -> Optional[str]:
        """Try a specific provider with retry logic."""
        if not provider or not api_key:
            return None
        
        provider_config = self.PROVIDERS[provider]
        
        # Increase timeout for longer requests (script generation)
        timeout = 300.0 if max_tokens > 5000 else 120.0
        
        # Retry configuration
        max_retries = 3
        base_delay = 2.0  # seconds
        
        for attempt in range(max_retries):
            try:
                async with httpx.AsyncClient(timeout=timeout) as client:
                    if provider_config["format"] == "openai":
                        return await self._chat_openai_format(
                            client, provider_config["url"], api_key, model, provider,
                            prompt, temperature, max_tokens
                        )
                    elif provider_config["format"] == "gemini":
                        return await self._chat_gemini_format(
                            client, provider_config["url"], api_key, model,
                            prompt, temperature, max_tokens
                        )
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 429:
                    # Rate limited - exponential backoff with jitter
                    delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
                    print(f"Rate limited ({provider}), retry {attempt + 1}/{max_retries} after {delay:.1f}s")
                    if attempt < max_retries - 1:
                        await asyncio.sleep(delay)
                        continue
                print(f"LLM request failed ({provider}): {e}")
                return None
            except Exception as e:
                print(f"LLM request failed ({provider}): {e}")
                return None
        
        return None
    
    async def _chat_openai_format(
        self, client: httpx.AsyncClient, url: str, api_key: str, model: str,
        provider: str, prompt: str, temperature: float, max_tokens: int
    ) -> Optional[str]:
        """Handle OpenAI-compatible APIs (Groq, OpenRouter, OpenAI)."""
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # OpenRouter requires additional headers
        if provider == "openrouter":
            headers["HTTP-Referer"] = "https://visual-explainer.app"
            headers["X-Title"] = "Visual Explainer Generator"
        
        response = await client.post(
            url,
            headers=headers,
            json={
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": temperature,
                "max_tokens": max_tokens
            }
        )
        response.raise_for_status()
        result = response.json()
        return result["choices"][0]["message"]["content"]
    
    async def _chat_gemini_format(
        self, client: httpx.AsyncClient, url_template: str, api_key: str,
        model: str, prompt: str, temperature: float, max_tokens: int
    ) -> Optional[str]:
        """Handle Google Gemini API."""
        url = url_template.format(model=model)
        url = f"{url}?key={api_key}"
        
        response = await client.post(
            url,
            headers={"Content-Type": "application/json"},
            json={
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {
                    "temperature": temperature,
                    "maxOutputTokens": max_tokens
                }
            }
        )
        response.raise_for_status()
        result = response.json()
        return result["candidates"][0]["content"]["parts"][0]["text"]


class TopicClassifier:
    """
    Classifies user prompts to ensure they fall within supported topics.
    Uses LLM for intelligent classification.
    """
    
    VALID_TOPICS = [
        "Mathematics",
        "Machine Learning", 
        "Algorithms",
        "Physics"
    ]
    
    CLASSIFICATION_PROMPT = """You are a topic classifier for an educational video generator.
Analyze the user's prompt and determine if it falls within these supported topics:
- Mathematics (calculus, algebra, linear algebra, statistics, geometry, etc.)
- Machine Learning (neural networks, gradient descent, backpropagation, etc.)
- Algorithms (sorting, searching, data structures, complexity, etc.)
- Physics (mechanics, waves, electricity, basic physics concepts)

User prompt: "{prompt}"

Respond in JSON format:
{{
    "is_valid": true/false,
    "topic": "Mathematics" | "Machine Learning" | "Algorithms" | "Physics" | "Invalid",
    "confidence": 0.0-1.0,
    "reason": "brief explanation"
}}

Only respond with valid JSON, nothing else."""

    def __init__(self):
        self.llm = LLMClient()
    
    async def classify(self, prompt: str) -> Dict:
        """
        Classify the prompt using LLM.
        Falls back to keyword matching if LLM fails.
        """
        # Try LLM classification first
        if self.llm.provider:
            try:
                return await self._classify_with_llm(prompt)
            except Exception as e:
                print(f"LLM classification failed: {e}, falling back to keywords")
        
        # Fallback to keyword-based classification
        return self._classify_with_keywords(prompt)
    
    async def _classify_with_llm(self, prompt: str) -> Dict:
        """Use LLM for classification."""
        content = await self.llm.chat(
            self.CLASSIFICATION_PROMPT.format(prompt=prompt),
            temperature=0.1,
            max_tokens=200
        )
        
        if not content:
            return self._classify_with_keywords(prompt)
        
        # Parse JSON response
        try:
            # Clean up potential markdown code blocks
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]
            
            classification = json.loads(content.strip())
            return {
                "is_valid": classification.get("is_valid", False),
                "topic": classification.get("topic", "Invalid"),
                "confidence": classification.get("confidence", 0.0),
                "reason": classification.get("reason", "")
            }
        except json.JSONDecodeError:
            return self._classify_with_keywords(prompt)
    
    def _classify_with_keywords(self, prompt: str) -> Dict:
        """Fallback keyword-based classification."""
        prompt_lower = prompt.lower()
        
        # Define keywords for each topic
        topic_keywords = {
            "Mathematics": [
                "math", "calculus", "derivative", "integral", "algebra", 
                "equation", "function", "graph", "polynomial", "matrix",
                "vector", "linear", "quadratic", "exponential", "logarithm",
                "trigonometry", "sine", "cosine", "geometry", "probability",
                "statistics", "limit", "series", "convergence", "divergence"
            ],
            "Machine Learning": [
                "machine learning", "ml", "neural network", "deep learning",
                "gradient descent", "backpropagation", "training", "model",
                "classification", "regression", "clustering", "cnn", "rnn",
                "transformer", "attention", "loss function", "optimization",
                "overfitting", "underfitting", "regularization", "dropout"
            ],
            "Algorithms": [
                "algorithm", "sorting", "searching", "binary search", "tree",
                "graph", "dfs", "bfs", "dynamic programming", "recursion",
                "complexity", "big o", "hash", "linked list", "stack", "queue",
                "heap", "dijkstra", "pathfinding", "divide and conquer"
            ],
            "Physics": [
                "physics", "force", "motion", "velocity", "acceleration",
                "gravity", "momentum", "energy", "wave", "frequency",
                "electricity", "magnetism", "circuit", "newton", "kinetic",
                "potential", "thermodynamics", "heat", "pressure"
            ]
        }
        
        # Check each topic
        scores = {}
        for topic, keywords in topic_keywords.items():
            score = sum(1 for kw in keywords if kw in prompt_lower)
            scores[topic] = score
        
        # Find best match
        best_topic = max(scores, key=scores.get)
        best_score = scores[best_topic]
        
        if best_score > 0:
            return {
                "is_valid": True,
                "topic": best_topic,
                "confidence": min(best_score / 3, 1.0),
                "reason": f"Matched {best_score} keywords for {best_topic}"
            }
        
        return {
            "is_valid": False,
            "topic": "Invalid",
            "confidence": 0.0,
            "reason": "No matching keywords found for supported topics"
        }


# Module-level function for backward compatibility
async def classify_topic(prompt: str) -> Optional[str]:
    classifier = TopicClassifier()
    result = await classifier.classify(prompt)
    return result["topic"] if result["is_valid"] else None