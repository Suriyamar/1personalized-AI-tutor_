# Personalized AI Tutor
![Python](https://img.shields.io/badge/python-3.10%2B-blue?logo=python) ![Streamlit](https://img.shields.io/badge/built%20with-Streamlit-fuchsia?logo=streamlit) ![Ollama](https://img.shields.io/badge/LLMs-local‑Ollama-orange) ![License](https://img.shields.io/badge/license-MIT-green)  
*A self‑hosted, LLM‑driven personalized learning platform that adapts to every learner.*

---

## 📖 Project Description
**Personalized AI Tutor** is an open‑source learning platform that uses local large‑language models (LLMs) to build **tailor‑made courses on demand**. Learners take a short pre‑assessment; the app then:
1. Designs a course outline that fits their knowledge level.
2. Streams in‑depth lesson content section‑by‑section.
3. Auto‑generates quizzes to lock in understanding.
4. Tracks progress locally—no cloud, no vendor lock‑in.

The platform showcases how on‑premise generative AI can enhance education while preserving privacy and controlling cost. The reference implementation runs comfortably on a consumer‑grade **NVIDIA RTX 3050** GPU, but will scale down to CPU‑only laptops (with slower generation times) or up to data‑center GPUs for real‑time output.

---

## ✨ Features at a Glance
| 💡 | Capability |
|----|------------|
| 🔐 | **Auth & Profiles** – registration, login, and per‑learner settings stored in CSV/JSON |
| 📝 | **Adaptive Pre‑Assessment** – 50 MCQs selected from grade‑specific banks |
| 🗺️ | **AI‑Generated Course Outline** – 4–6 modules with clear learning goals |
| 📚 | **Streaming Lesson Writer** – ≥ 2 500‑word module content with beginner/intermediate/advanced tone |
| ❓ | **Quiz Builder & Grader** – 10 fresh MCQs per module with instant feedback |
| 📊 | **Progress Tracker** – completion status & scores saved locally |
| 🧭 | **Intuitive Sidebar Navigation** – jump between outline, content, and quizzes |

---

## 🏗️ How It Works
```
┌────────────┐      login / register      ┌──────────────────┐
│  Browser   │  ───────────────────────▶ │ Streamlit Front‑ │
└────────────┘                           │     End          │
      ▲                                   └────────┬────────┘
      │   websocket/HTTP                             │
      │                                              ▼
      │                                   Business Logic (pages/*)
      │                                              │
      │                                              ▼
      │                                   ┌───────────────────────┐
      │                                   │  Local LLM Engines    │
      │                                   │  • Gemma‑2B (outline) │
      │                                   │  • Llama‑3 8B (lessons)│
      │                                   │  • Gemma‑2B (quizzes) │
      │                                   └───────────────────────┘
      │                                              │
      │                                              ▼
      │                                   CSV / JSON persistence
      │                                              │
      ▼                                              ▼
 Local Filesystem  ◀────── per‑user courses & scores ─┘
```

---

## ⚙️ Tech Stack
| Layer | Tooling |
|-------|---------|
| **Frontend** | Streamlit multipage app |
| **LLM Serving** | [Ollama](https://github.com/jmorganca/ollama) running Gemma 2B & Llama 3 8B |
| **Data Storage** | CSV / JSON (SQLite upgrade planned) |
| **Parsing** | Regex & custom heuristics for deterministic cleanup |
| **Packaging** | `requirements.txt` & optional Docker Compose |

---

## 🏫 Program Context & Hardware
| Hardware Tier | Typical Latency* |
|---------------|-----------------|
| **RTX 3050 / 8 GB VRAM** | 30–60 s per 2 500‑word module |
| **CPU‑only / integrated GPU** | 2–4× slower (lower batch size recommended) |
| **RTX 4090 / A100** | 5–10 s per module (near real‑time) |

> *Measured with default generation parameters; your mileage may vary.*

### Tips for Low‑VRAM Systems
* Switch `llama3:8b` → `llama3:8b‑q4_0` or a 3‑5 B model in `course_content_gen.py`.
* Reduce `num_questions` in `mcq_gen.py` to cut prompt + output length.
* Disable image generation or additional context retrieval steps.

---

## 🚀 Quick Start
```bash
# 1) Clone the repo
$ git clone https://github.com/your‑org/unnati.git && cd unnati

# 2) Create & activate a virtual environment
$ python -m venv .venv
$ source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 3) Install Python dependencies
$ pip install -r requirements.txt

# 4) Pull the required LLMs (first‑time only)
$ ollama pull llama3:8b
$ ollama pull gemma:2b

# 5) Run the app
$ streamlit run main.py
```
Visit **http://localhost:8501** in your browser and create an account to begin.

### 🐳 Docker (optional)
```bash
docker compose up --build  # builds image, pulls models, and serves at :8501
```
*Requires ~6 GB RAM + model storage.*

---

## 📂 Project Layout
```text
.
├── auth/                       # Authentication helpers
│   ├── login.py
│   ├── register.py
│   └── profiles.py
├── pages/                      # Streamlit multipage UIs
│   ├── login_ui.py             # Login / Register interface
│   ├── preassessment_ui.py     # Adaptive pre‑assessment test
│   ├── content_ui.py           # Lesson streaming & course flow
│   ├── mcq_ui.py               # Module quizzes & grading
│   └── sidebar.py              # Navigation rail
├── preassessment/              # MCQ banks (CSV)
│   ├── Elementary_MCQ_Full_Set.csv
│   ├── Middle_School_MCQ_Test_Full.csv
│   └── High_School_MCQ_Test_Full.csv
├── users/                      # Populated at runtime (per‑user data)
├── course_gen.py               # AI outline generator (Gemma‑2B)
├── course_content_gen.py       # AI lesson generator (Llama‑3 8B)
├── mcq_gen.py                  # AI quiz generator (Gemma‑2B)
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Container build (optional)
└── main.py                     # Streamlit entrypoint
```

---

## 🧩 Module Breakdown

### Authentication (`auth/`)
* **login.py** – Validates credentials against `users.csv` and returns the matching row.
* **register.py** – Adds a new user, prevents duplicates, and scaffolds `users/<username>/` directories.
* **profiles.py** – Retrieves stored profile details for downstream pages.

### Core AI Engines
* **course_gen.py** *(Gemma‑2B)* – Streams a 4–6‑module outline via `generate_outline_stream()`.
* **course_content_gen.py** *(Llama‑3 8B)* – Produces ≥ 2 500‑word lessons tuned to learner difficulty.
* **mcq_gen.py** *(Gemma‑2B)* – Generates exactly *n* MCQs in a strict markdown format with answer keys.

### Streamlit UI Pages (`pages/`)
* **login_ui.py** – Tabbed login & registration interface; populates `st.session_state` on success.
* **preassessment_ui.py** – Serves the adaptive 50‑question MCQ test, scores it, and stores results in `users/data/<username>.json`.
* **content_ui.py** – Streams lesson content chunk‑by‑chunk, saves `module_X_content.txt`, and updates completion status.
* **mcq_ui.py** – Generates quizzes via `generate_mcq()`, renders radio buttons, grades answers, and logs scores to `users/<username>/scores/completed_modules.csv`.
* **sidebar.py** – Context‑aware navigation rail; updates `st.query_params` for deep‑links.

### Data Assets
* **preassessment/** – Three CSV banks (Elementary, Middle, High) with columns `Question, Option A–D, Answer Key`.

### Runtime Storage (`users/`)
```text
users/
└── <username>/
    ├── courses/
    │   └── <course_topic>/
    │       ├── <topic>.outline
    │       └── module_1_content.txt …
    ├── scores/
    │   └── completed_modules.csv
    └── data/<username>.json   # pre‑assessment & profile extras
```

### Entry Point
* **main.py** – Configures Streamlit (`st.set_page_config`), checks login state, and launches the Outline Generator page when authenticated.

---

## 🔧 Configuration
```env
# .env (optional) – override defaults
OLLAMA_HOST=http://localhost:11434
USERS_ROOT=./users
PREASSESSMENT_BANK=./preassessment
```
All variables can also be exported directly in your shell.

---

## 🔬 Advanced Usage
### Switching Models
* **Smaller / Faster:** Replace `llama3:8b` with `mistral:7b` or `phi3:4b`.
* **Higher Quality:** Point to a local `mixtral‑8x22b` if you have ≥48 GB VRAM.

### Custom Question Banks
Drop CSVs into `/preassessment` with columns:
```
Question,Option A,Option B,Option C,Option D,Answer Key
```
File names should follow the pattern `<Level>_MCQ_*.csv`.

### Adding Multimedia
The lesson generator prompt can be extended to include image placeholders or embedded videos. Update `course_content_gen.py` accordingly.

---


## 🧪 Tests
```bash
$ pytest -q        # run unit tests under /tests
```
Add tests when submitting PRs; mocks are provided for Ollama calls.

---

## 🤝 Contributing
We welcome pull requests!  Please:
1. Fork ➜ create feature branch ➜ commit with clear messages.
2. Ensure `pytest` passes and `pre‑commit` hooks (black, flake8) succeed.
3. Update docs / examples if behaviour changes.

Join the discussion in the **Issues** tab if you have ideas or questions.

---

## 📜 License
Released under the **MIT License** — see `LICENSE` for details.

---

> Built with ❤️ , LLMs, and plenty of coffee for the Intel Unnati showcase.
