<div align="center">
  <img src="./readme-images/full-logo.png" alt="Nimator Logo" width="200" />

  # Nimator
  
  **Transform Text into Math & Physics Animations Instantly**
  
  <p align="center">
    <a href="https://nextjs.org">
      <img src="https://img.shields.io/badge/Next.js-14-black?style=for-the-badge&logo=next.js&logoColor=white" alt="Next.js" />
    </a>
    <a href="https://fastapi.tiangolo.com">
      <img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI" />
    </a>
    <a href="https://www.python.org/">
      <img src="https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
    </a>
    <a href="https://www.manim.community/">
      <img src="https://img.shields.io/badge/Manim-Rendering-critical?style=for-the-badge&logo=youtube&logoColor=white" alt="Manim" />
    </a>
  </p>

  [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
  [![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker&logoColor=white)](https://docker.com)
  [![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
  [![Prettier](https://img.shields.io/badge/code_style-prettier-ff69b4.svg?logo=prettier)](https://github.com/prettier/prettier)

  <p align="center">
    <a href="#-demo">Demo</a> •
    <a href="#-features">Features</a> •
    <a href="#-tech-stack">Tech Stack</a> •
    <a href="#-getting-started">Getting Started</a> •
    <a href="#-architecture">Architecture</a>
  </p>
</div>

---

## 💡 Overview

**Nimator** (formerly Visual Explainer Generator) is a cutting-edge educational tool that democratizes high-quality animated explanations. By bridging **Large Language Models (LLMs)** with the **Manim** animation engine, Nimator converts simple natural language queries into professional, mathematically accurate video explanations in seconds.

Whether you're a student struggling with Calculus or a developer revising Algorithms, Nimator visualizes the abstract.

## 📺 Demo

<div align="center">
  <img src="./readme-images/video.gif" alt="Project Demo" width="80%" style="border-radius: 10px; box-shadow: 0 10px 30px rgba(0,0,0,0.15);">
</div>

<br />

## ✨ Features

| Feature | Description |
| :--- | :--- |
| 🗣️ **Natural Language Input** | Simply type "Explain Gradient Descent" and watch the magic happen. |
| 🎬 **Auto-Generated Scripts** | LLMs craft the educational narrative and Python code for animations simultaneously. |
| 🖌️ **Visual-First Learning** | Uses **Manim** to render vector-quality graphs, mathematical proofs, and physics simulations. |
| 🎙️ **AI Voiceover** | Integrated Text-to-Speech (TTS) narrating every step of the explanation. |
| ⚡ **Real-time Processing** | Asynchronous job queues with Redis ensure smooth handling of multiple requests. |
| 📦 **Dockerized** | One-command deployment for the entire stack. |

## � Tech Stack

### Frontend
![React](https://img.shields.io/badge/React-20232A?style=flat&logo=react&logoColor=61DAFB)
![Next.js](https://img.shields.io/badge/Next.js-black?style=flat&logo=next.js&logoColor=white)
![TypeScript](https://img.shields.io/badge/TypeScript-007ACC?style=flat&logo=typescript&logoColor=white)
![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=flat&logo=tailwind-css&logoColor=white)
![Framer Motion](https://img.shields.io/badge/Framer_Motion-0055FF?style=flat&logo=framer&logoColor=white)

### Backend & AI
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=flat&logo=fastapi)
![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)
![Manim](https://img.shields.io/badge/Manim-Engine-red?style=flat&logo=youtube&logoColor=white)
![NumPy](https://img.shields.io/badge/NumPy-013243?style=flat&logo=numpy&logoColor=white)
![SymPy](https://img.shields.io/badge/SymPy-brightgreen?style=flat&logo=sympy&logoColor=white)

### Infrastructure
![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat&logo=docker&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-DC382D?style=flat&logo=redis&logoColor=white)

## 🚀 Getting Started

Follow these steps to set up the project locally.

### Prerequisites
- **Docker** & **Docker Compose** installed.
- (Optional) **Groq API Key** for LLM capabilities.

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/pavank-code/Nimator.git
   cd Nimator
   ```

2. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env and allow adding your GROQ_API_KEY if you have one
   ```

3. **Run with Docker** (Recommended)
   ```bash
   docker-compose up --build
   ```

   > ⏳ **Note**: The first build might take a few minutes as it pulls the Manim docker image and installs dependencies.

4. **Access the Application**
   - 🖥️ **Frontend**: [http://localhost:3000](http://localhost:3000)
   - ⚙️ **Backend API**: [http://localhost:8000/docs](http://localhost:8000/docs)

## 🏗 Architecture

The system follows a microservices architecture to separate the heavy rendering logic from the user-facing application.

```mermaid
graph LR
    A[Frontend Client] -- HTTP --> B[FastAPI Backend]
    B -- Enqueue Job --> C[Redis Queue]
    C -- Dequeue Job --> D[Manim Worker]
    D -- Generate --> E[MP4 Video]
    E -- Serve --> A
    B -- LLM Calls --> F[Groq/OpenAI]
```

1.  **Job Queue System**: Redis manages the workload, preventing server crashes during heavy rendering tasks.
2.  **Stateless API**: FastAPI ensures scalablity.
3.  **Isolated Renderer**: The rendering engine runs in its own container with all system dependencies (LaTeX, FFmpeg) pre-packaged.

## � Screenshots

<div align="center">
  <table>
    <tr>
      <td align="center">
        <b>Generation Interface</b><br>
        <img src="./readme-images/screenshot1.png" alt="Generate Screen" width="400">
      </td>
      <td align="center">
        <b>Processing & Result</b><br>
        <img src="./readme-images/screenshot2.png" alt="Status Screen" width="400">
      </td>
    </tr>
  </table>
</div>

## 🎯 Supported Topics

Our model performs best with:
- ✅ **Calculus** (Derivatives, Integrals)
- ✅ **Linear Algebra** (Vectors, Matrices)
- ✅ **sorting Algorithms** (Bubble Sort, Merge Sort)
- ✅ **Physics Mechanics** (Projectile Motion, Forces)

## 🤝 Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

---

<div align="center">
  <sub>Built with ❤️ by the Nimator Team</sub>
</div>
