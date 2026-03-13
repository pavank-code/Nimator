# Complete AI Stack Inventory - Visual Explainer Generator

## Overview
The system uses a **Two-Stage Pipeline** orchestrated by a **Multi-Provider LLM Architecture** with both **reasoning** and **code generation** AI models, plus **TTS** for voiceover.

---

## 1. CORE AI PROVIDERS & MODELS

### 1.1 PRIMARY: NVIDIA NIM - DeepSeek V3.2 (REASONING MODEL)
**Role:** Script generation, visual-first pedagogy, topic analysis
**API Endpoint:** `https://integrate.api.nvidia.com/v1/chat/completions`
**Model:** `deepseek-ai/deepseek-v3.2`
**API Key:** `<REDACTED>`
**Config Keys:**
- `NVIDIA_DEEPSEEK_API_KEY`
- `NVIDIA_DEEPSEEK_MODEL`

**Capabilities:**
- Long-context reasoning (360-480 second video scripts)
- Visual-first pedagogy generation
- Structured JSON output (scripts with voiceover + visual descriptions)
- Temperature: 0.7 for creative script generation
- Max tokens: 12,000 (for full-length videos)

---

### 1.2 SECONDARY: NVIDIA NIM - Qwen 2.5 Coder 32B (CODE SPECIALIST)
**Role:** Manim scene specification generation, code validation, debugging (future)
**API Endpoint:** `https://integrate.api.nvidia.com/v1/chat/completions`
**Model:** `qwen/qwen2.5-coder-32b-instruct`
**API Key:** `<REDACTED>`
**Config Keys:**
- `NVIDIA_QWEN_API_KEY`
- `NVIDIA_QWEN_MODEL`

**Capabilities:**
- Python/Manim code generation
- JSON schema validation
- Animation parameter optimization
- Temperature: 0.3 for deterministic scene specs
- Max tokens: 1,500 (per scene)

---

### 1.3 FALLBACK #1: Google Gemini
**Role:** Backup for script and scene generation
**API Endpoint:** `https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent`
**Model:** `gemini-2.0-flash`
**API Key:** `<REDACTED>`
**Config Keys:**
- `GEMINI_API_KEY`
- `GEMINI_MODEL`

---

### 1.4 FALLBACK #2: Groq (LLaMA 3.3 70B)
**Role:** Alternative fast inference provider
**API Endpoint:** `https://api.groq.com/openai/v1/chat/completions`
**Model:** `llama-3.3-70b-versatile`
**Config Keys:**
- `GROQ_API_KEY`
- `GROQ_MODEL`

---

### 1.5 FALLBACK #3: OpenRouter (Xiaomi MiMo-V2-Flash)
**Role:** Free tier alternative with large context window
**API Endpoint:** `https://openrouter.ai/api/v1/chat/completions`
**Model:** `xiaomi/mimo-v2-flash:free`
**API Key:** `<REDACTED>`
**Config Keys:**
- `OPENROUTER_API_KEY`
- `OPENROUTER_MODEL`

---

### 1.6 FALLBACK #4: OpenAI (GPT-4o Mini)
**Role:** Paid alternative fallback
**API Endpoint:** `https://api.openai.com/v1/chat/completions`
**Model:** `gpt-4o-mini`
**Config Keys:**
- `OPENAI_API_KEY`
- `OPENAI_MODEL`

---

## 2. PIPELINE AI API CALLS

### 2.1 Stage 1: Script Generation (ScriptWriter)

**File:** `backend/app/services/script_writer.py`

#### Call 1: Topic Classification
- **LLM:** DeepSeek V3.2 (via LLMClient)
- **Function:** `TopicClassifier.classify(prompt)`
- **Prompt:** `CLASSIFICATION_PROMPT` - Analyzes user prompt against valid topics
- **Temperature:** 0.1 (deterministic)
- **Max Tokens:** 200
- **Output:** JSON with `{is_valid, topic, confidence, reason}`
- **Used in:** `backend/app/api/routes.py` line ~70

#### Call 2: Script Generation - Full Videos
- **LLM:** DeepSeek V3.2 (primary)
- **Function:** `ScriptWriter.generate_script(prompt, sample_mode, duration_seconds)`
- **Prompt:** `SCRIPT_GENERATION_PROMPT`
- **Features:**
  - Visual-first pedagogy rules
  - HOOK → FOUNDATION → CORE → INSIGHTS → SUMMARY structure
  - 25-35 scenes for full-length videos
  - JSON output with synchronized voiceover + visual descriptions
- **Temperature:** 0.7 (creative)
- **Max Tokens:** 12,000 (long context)
- **Output Schema:**
  ```json
  {
    "title": string,
    "total_duration_seconds": int,
    "summary": string,
    "scenes": [
      {
        "scene_number": int,
        "duration_seconds": int,
        "voiceover": string,
        "visual_description": string,
        "visual_type": "graph_2d | vector_arrows | dots_paths | text_labels",
        "visual_elements": {...},
        "sync_points": [...]
      }
    ]
  }
  ```

#### Call 3: Script Generation - Sample Videos (30s)
- **LLM:** DeepSeek V3.2
- **Function:** `ScriptWriter._generate_sample_script(prompt, duration_seconds)`
- **Prompt:** `SAMPLE_SCRIPT_PROMPT`
- **Features:**
  - Short format: 3 scenes × 10 seconds
  - High visual impact
  - Deterministic structure
- **Temperature:** 0.8 (slightly more creative than full)
- **Max Tokens:** 3,000
- **Used in:** `backend/app/services/scene_planner.py` line ~40

---

### 2.2 Stage 2: Manim Code Generation (ManimCodeGenerator)

**File:** `backend/app/services/manim_code_generator.py`

#### Call 4: Per-Scene Manim Parameter Generation
- **LLM:** Qwen 2.5 Coder (intended for future; currently using auto-detect LLM)
- **Function:** `ManimCodeGenerator._generate_single_scene(script_scene, colors)`
- **Prompt:** `SCENE_GENERATION_PROMPT`
- **Features:**
  - Converts voiceover + visual description → Manim parameters
  - Validates against 4 scene types: `graph_2d`, `vector_arrows`, `dots_paths`, `text_labels`
  - Injects color palette for visual variety
  - Function library with diverse math expressions
- **Temperature:** 0.3 (deterministic)
- **Max Tokens:** 1,500 (per scene)
- **Called:** Once per script scene (3-35 times per video)
- **Output Schema:**
  ```json
  {
    "scene_type": "graph_2d | vector_arrows | dots_paths | text_labels",
    "title": string,
    "narration": string (exact voiceover copy),
    "color": hex_string,
    // ... scene-type-specific params
  }
  ```

---

## 3. TEXT-TO-SPEECH (TTS) AI

### 3.1 Deepgram Aura (Primary)
**File:** `renderer/app/tts/voiceover.py`

**Role:** High-quality AI voice generation for voiceover

**API Endpoint:** `https://api.deepgram.com/v1/speak?model={voice}`

**API Key:** `784aa1f5dbcb34355d391473f2e85fa14c06c8a6`

**Voice:** `aura-orion-en` (male, deep, professional)

**Available Voices:**
- Female: asteria, luna, stella, athena, hera
- Male: orion, arcas, perseus, angus, orpheus, helios, zeus

**Function Call:**
```python
VoiceoverGenerator.generate(text, file_prefix)
  └─> _generate_deepgram(text, output_path)
      └─> POST to https://api.deepgram.com/v1/speak
          Body: {"text": text}
          Returns: MP3 audio bytes
```

**Features:**
- LaTeX → natural language conversion
- Math symbol replacement (√, ∞, α, β, etc.)
- Automatic caching by text hash
- Timeout: 60 seconds

**Fallback:** gTTS (Google Text-to-Speech) if Deepgram fails

---

## 4. ORCHESTRATOR ARCHITECTURE

### 4.1 Current Flow
```
User Prompt (API)
    ↓
Topic Classifier (DeepSeek) → Classification
    ↓
Scene Planner (Orchestrator)
    ├─→ Script Writer (DeepSeek) → Full Script + Voiceover
    └─→ Manim Code Generator (Qwen/Auto-detect) → Scene Specs
    ↓
Job Orchestrator (Redis Queue)
    ↓
Renderer Worker
    ├─→ Voiceover Generator (Deepgram TTS)
    ├─→ Manim Scene Rendering
    └─→ Video Assembly
    ↓
Frontend (Download Video)
```

### 4.2 LLMClient (Multi-Provider)
**File:** `backend/app/services/topic_classifier.py`

**Class:** `LLMClient`

**Provider Registry:**
```python
PROVIDERS = {
    "nvidia": {...},              # DeepSeek (default)
    "nvidia_deepseek": {...},     # Explicit DeepSeek
    "nvidia_qwen": {...},         # Explicit Qwen
    "groq": {...},
    "openrouter": {...},
    "openai": {...},
    "gemini": {...}
}
```

**Agent Types (for future orchestrator):**
- `LLMClient(agent_type="default")` → Auto-detect best provider
- `LLMClient(agent_type="deepseek")` → Force NVIDIA DeepSeek
- `LLMClient(agent_type="qwen")` → Force NVIDIA Qwen

**Fallback Chain:**
1. Primary provider (configured in `LLM_PROVIDER`)
2. Fallback list: `nvidia → groq → openrouter → openai → gemini`
3. Retry logic: 3 attempts with exponential backoff on rate limits (429)
4. Timeout: 300s for long requests (>5000 tokens), 120s otherwise

---

## 5. API ENDPOINTS

### 5.1 Backend API (http://localhost:8000)

#### POST /api/generate
**AI Calls:**
1. Topic Classification (DeepSeek)
2. Scene Planning (DeepSeek → Qwen)
3. Validation

**Response:**
```json
{
  "job_id": "uuid",
  "message": "Video generation started successfully",
  "status": "queued"
}
```

#### GET /api/status/{job_id}
**Returns:** Job status, progress, video URL

#### GET /api/video/{job_id}
**Returns:** Video metadata (topic, prompt, URL)

#### GET /health
**Returns:** `{"status": "healthy"}`

---

## 6. CONFIGURATION SUMMARY

### Environment Variables (.env)
```
# Primary AI
NVIDIA_API_KEY=<REDACTED>
NVIDIA_DEEPSEEK_API_KEY=<REDACTED>
NVIDIA_QWEN_API_KEY=<REDACTED>

# TTS
DEEPGRAM_API_KEY=<REDACTED>

# Fallbacks
OPENROUTER_API_KEY=<REDACTED>
GEMINI_API_KEY=<REDACTED>
```

### Config Settings (config.py)
```python
LLM_PROVIDER="nvidia"  # Auto, or: nvidia, groq, openrouter, openai, gemini

# Models
NVIDIA_DEEPSEEK_MODEL="deepseek-ai/deepseek-v3.2"
NVIDIA_QWEN_MODEL="qwen/qwen2.5-coder-32b-instruct"

# Generation
MAX_SCENES=100
MIN_SCENES_REQUIRED=10
TARGET_GENERATION_TIME=600  # 10 min
RENDER_TIMEOUT=60  # per scene
```

---

## 7. FUTURE ARCHITECTURE CHANGES (READY FOR)

### Orchestrator & State Management
The codebase is already prepared for:

1. **Agent Specialization:**
   - DeepSeek: Reasoning, script generation, topic analysis
   - Qwen: Manim code generation, validation, debugging

2. **System Prompts (Ready to Add):**
   ```python
   NVIDIA_DEEPSEEK_SYSTEM_PROMPT = "You are a visual-first AI tutor..."
   NVIDIA_QWEN_SYSTEM_PROMPT = "You are a Manim code specialist..."
   ```

3. **State Management (Via Redis):**
   - Job state tracking
   - Agent communication queue
   - Result caching

4. **Explicit Agent Selection:**
   ```python
   deepseek_client = LLMClient(agent_type="deepseek")
   qwen_client = LLMClient(agent_type="qwen")
   ```

---

## 8. CURRENT BOTTLENECKS & OPPORTUNITIES

### Performance
- **Script generation:** 15-30s (LLM latency)
- **Scene generation:** 1-2s per scene (LLM overhead)
- **Rendering:** 5-10s per scene (CPU-bound, not AI)

### Optimization Opportunities
1. **Batching:** Generate multiple scenes in parallel
2. **Caching:** Store generated scripts for common topics
3. **Agent-specific prompts:** Use system prompts for each model
4. **State machine:** Explicit orchestrator for agent coordination

---

## SUMMARY TABLE

| Component | AI Provider | API Key | Role | Call Frequency |
|-----------|-------------|---------|------|-----------------|
| **Script Writer** | DeepSeek V3.2 | NVIDIA | Voiceover + visuals | 1x per video |
| **Scene Generator** | Qwen 2.5 / Auto | NVIDIA | Manim parameters | 3-35x per video |
| **Topic Classifier** | DeepSeek V3.2 | NVIDIA | Input validation | 1x per request |
| **Voiceover** | Deepgram Aura | Deepgram | TTS (aura-orion-en) | 3-35x per video |
| **Fallback 1** | Gemini 2.0 Flash | Google | Backup LLM | On failure |
| **Fallback 2** | LLaMA 3.3 70B | Groq | Fast backup | On failure |
| **Fallback 3** | Xiaomi MiMo | OpenRouter | Free alternative | On failure |

---

**Last Updated:** January 24, 2026  
**Ready for:** Multi-agent orchestrator, system prompts, advanced state management
