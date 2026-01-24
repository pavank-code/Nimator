# Visual Explainer Generator 🎬

Transform complex concepts into clear, animated visual explanations.

![MIT License](https://img.shields.io/badge/License-MIT-green.svg)
![Python 3.11+](https://img.shields.io/badge/Python-3.11+-blue.svg)
![Next.js 14](https://img.shields.io/badge/Next.js-14-black.svg)

## 🎯 Overview

Visual Explainer Generator converts natural language questions into short (30-90 second) animated videos. It's designed for math, algorithms, ML, and physics concepts - providing visual-first explanations using programmatic animations (Manim).

## ✨ Features

- **Natural Language Input**: Just describe what you want to understand
- **Visual-First Explanations**: Animated graphs, vectors, and diagrams
- **No Account Required**: Start generating immediately
- **Voiceover Narration**: Automated TTS for each scene
- **Download MP4**: Keep your videos for offline use

## 🎯 Supported Topics

- ✅ Mathematics (calculus, linear algebra, statistics)
- ✅ Machine Learning (gradient descent, neural networks)
- ✅ Algorithms (sorting, searching, data structures)
- ✅ Physics (mechanics, basic concepts)

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose
- (Optional) Groq API key for enhanced LLM features

### 1. Clone and Configure

```bash
git clone <repository-url>
cd visual-explainer-generator

# Copy environment template
cp .env.example .env

# (Optional) Add your Groq API key to .env
# Get free key at: https://console.groq.com/
```

### 2. Start with Docker Compose

```bash
docker-compose up --build
```

### 3. Open the App

- **Frontend**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs

## 🏗️ Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│    Frontend     │────▶│    Backend      │────▶│    Renderer     │
│   (Next.js)     │     │   (FastAPI)     │     │    (Manim)      │
│   Port 3000     │     │   Port 8000     │     │                 │
└─────────────────┘     └────────┬────────┘     └─────────────────┘
                                 │
                        ┌────────▼────────┐
                        │      Redis      │
                        │   (Job Queue)   │
                        │   Port 6379     │
                        └─────────────────┘
```

### Components

| Component | Tech Stack | Purpose |
|-----------|------------|---------|
| Frontend | Next.js 14, React, Tailwind | User interface |
| Backend | FastAPI, Python 3.11 | API, job orchestration, LLM calls |
| Renderer | Manim, FFmpeg, gTTS | Scene rendering, video assembly |
| Queue | Redis | Job management between backend & renderer |

## 📁 Project Structure

```
visual-explainer-generator/
├── frontend/           # Next.js frontend
│   ├── src/
│   │   ├── app/       # Pages
│   │   └── components/ # React components
│   └── Dockerfile
├── backend/            # FastAPI backend
│   ├── app/
│   │   ├── api/       # API routes
│   │   ├── services/  # Business logic
│   │   └── models/    # Data models
│   └── Dockerfile
├── renderer/           # Manim renderer
│   ├── app/
│   │   ├── manim_scenes/ # Scene templates
│   │   ├── tts/       # Voice generation
│   │   └── assembler/ # Video assembly
│   └── Dockerfile
├── shared/             # Shared schemas
└── docker-compose.yml
```

## 🔧 Development Setup

### Local Development (without Docker)

#### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

#### Frontend
```bash
cd frontend
npm install
npm run dev
```

#### Renderer (requires Manim dependencies)
```bash
cd renderer
pip install -r requirements.txt
# Install system deps: ffmpeg, latex, cairo
python -m app.worker
```

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `GROQ_API_KEY` | - | Groq API key for LLM (optional, uses fallback) |
| `REDIS_HOST` | redis | Redis hostname |
| `REDIS_PORT` | 6379 | Redis port |
| `MAX_SCENES` | 6 | Maximum scenes per video |
| `RENDER_TIMEOUT` | 20 | Seconds per scene timeout |

## 🎨 Scene Types

The renderer supports 4 scene types:

1. **graph_2d**: Function plots with optional moving dots
2. **vector_arrows**: Vector visualizations
3. **dots_paths**: Points moving along paths
4. **text_labels**: Text and LaTeX formulas

## 📊 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/generate` | Start video generation |
| GET | `/api/status/{job_id}` | Get job status |
| GET | `/api/video/{job_id}` | Get completed video info |
| GET | `/videos/{id}.mp4` | Download video file |

## 🔒 MVP Constraints

- Maximum 6 scenes per video
- 300 character prompt limit
- Only predefined animation types
- Videos auto-delete after 1 hour
- No user accounts

## 🐛 Troubleshooting

### Common Issues

**"Redis connection refused"**
- Ensure Redis is running: `docker-compose up redis`

**"Failed to render scene"**
- Check renderer logs: `docker-compose logs renderer`
- Ensure LaTeX is installed for math rendering

**"Topic not supported"**
- The MVP only supports math/tech topics
- Try rephrasing with math/algorithm keywords

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

## 🙏 Acknowledgments

- [Manim](https://www.manim.community/) - Animation engine
- [Groq](https://groq.com/) - Fast LLM inference
- [gTTS](https://gtts.readthedocs.io/) - Text-to-speech