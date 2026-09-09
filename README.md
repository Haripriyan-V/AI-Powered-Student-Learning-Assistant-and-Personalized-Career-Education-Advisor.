# 🎓 DishaAI – AI-Powered Student Skill & Career Intelligence Platform

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)
![React](https://img.shields.io/badge/React-18-61DAFB?logo=react)
![Django](https://img.shields.io/badge/Django-5.0-092E20?logo=django)
![Vite](https://img.shields.io/badge/Vite-5.0-646CFF?logo=vite)
![TailwindCSS](https://img.shields.io/badge/TailwindCSS-3.4-38B2AC?logo=tailwind-css)
![License](https://img.shields.io/badge/License-MIT-orange)

An intelligent, next-generation web platform that unifies academic learning, skill assessment, career recommendation, ATS resume analysis, and gamified progress tracking around a central **AI Skill Gap Analyzer**.

---

## 🌟 Key Platform Capabilities

```
                       ┌────────────────────────────────────────────────────────┐
                       │               STUDENT 360° PROFILE                     │
                       │   (Target Career, Verified Skills, XP, Streak, Resume) │
                       └──────────────────────────┬─────────────────────────────┘
                                                  │
                ┌─────────────────────────────────┼─────────────────────────────────┐
                ▼                                 ▼                                 ▼
    ┌───────────────────────┐         ┌───────────────────────┐         ┌───────────────────────┐
    │  AI RESUME ANALYZER   │         │ ⭐ AI SKILL GAP        │         │ AI CAREER RECOMMENDER │
    │ • ATS Score (0-100)   │         │    ANALYZER           │         │ • 5-Factor Alignment  │
    │ • Normalized Skills   │────────▶│ • Radar & Gauge Chart │◀────────│ • Transparent Scoring │
    │ • 1-Click Import CTA  │         │ • Priority Algorithm  │         │ • Target Role Lock    │
    └───────────────────────┘         │ • 5-Tier Gaps Class   │         └───────────────────────┘
                                      └───────────┬───────────┘
                                                  │
                ┌─────────────────────────────────┴─────────────────────────────────┐
                ▼                                                                   ▼
    ┌───────────────────────┐                                           ┌───────────────────────┐
    │ ADAPTIVE ROADMAP      │                                           │ CONTEXT-AWARE CHATBOT │
    │ • 4 Dynamic Phases    │                                           │ • 360° Profile Context│
    │ • Task Completion     │                                           │ • Markdown & Chips    │
    │ • +15% Skill Bump     │                                           │ • Skill Mentorship    │
    └───────────┬───────────┘                                           └───────────────────────┘
                ▼
    ┌───────────────────────┐
    │ GAMIFICATION & XP     │
    │ • XP, Levels, Badges  │
    │ • 7-Day Streaks       │
    │ • Real-time Feedback  │
    └───────────────────────┘
```

### 1. ⭐ AI Skill Gap Analyzer (Platform Core)
- **Mathematical Gap Scoring**:
  $$\text{Gap Score} = \max(0, \text{Required Score} - \text{Current Score})$$
  $$\text{Priority Score} = \text{Importance} \times \text{Gap Score} \times \text{Career Relevance}$$
- **5-Tier Severity Classification**:
  - 🟢 **Strong Skill**: Gap $\le 0$ (exceeds or meets role benchmarks)
  - 🟡 **Minor Gap**: Gap $\le 20\%$
  - 🟠 **Moderate Gap**: Gap $\le 40\%$
  - 🔴 **Major Gap**: Gap $\le 60\%$
  - 🟣 **Critical Missing**: Current proficiency is 0% with importance $\ge 70\%$
- **Visual Intelligence**: Radar chart visualization comparing Current vs. Target Career Benchmarks, Overall Readiness Gauge, and Actionable AI Recommendations.

### 2. 🤖 360° Context-Aware AI Chat Assistant
- Injected with live student profile state: target role, readiness score, top skill gaps, current roadmap phase, and gamification level.
- Rich Markdown rendering with code blocks, tables, and lists.
- Dynamic quick-prompt suggestion chips tailored to current skill deficits.

### 3. 📄 AI Resume Analyzer
- Automated parsing of PDF, DOCX (native XML extraction), and TXT files.
- ATS scoring engine based on structural completeness, quantifiable metrics, keywords, and skill density.
- Normalized skill extraction with **1-Click Import to Student Skill Profile** that immediately updates the Skill Gap Analyzer.

### 4. 🎯 Transparent Career Recommendation Engine
- Multi-factor deterministic scoring:
  - Skill Overlap (40%)
  - Readiness / Proficiency Alignment (25%)
  - Academic & Background Relevance (15%)
  - Interest Alignment (10%)
  - Market Outlook & Demand (10%)
- Explains *why* each career fits with bulleted reasons and lets students set their primary **Target Career**.

### 5. 🗺️ Personalized Dynamic Learning Roadmap
- Automatically partitioned into 4 progressive phases:
  1. *Foundation & Core Prerequisites*
  2. *Core Domain Competencies*
  3. *Advanced & Applied Projects*
  4. *Career Readiness & Portfolio*
- **Adaptive Feedback Loop**: Completing a roadmap task bumps skill proficiency (+15%), awards XP (+50 XP), logs activity, and recalculates career readiness in real time.

### 6. 🏆 Student Progress & Gamification Center
- XP leveling ladder (Novice, Apprentice, Practitioner, Specialist, Master, Legend).
- 7-day interactive streak tracker with daily check-in reward (+15 XP).
- Unlockable achievement badges (e.g., *Fast Learner*, *Gap Crusher*, *Resume Ready*, *Roadmap Warrior*).
- Full learning activity audit log.

---

## 🛠️ Technology Stack

| Layer | Technologies |
|---|---|
| **Frontend** | React 18, Vite 5, TailwindCSS 3.4, Framer Motion, Recharts, Lucide / Heroicons, React Markdown |
| **Backend** | Python 3.11, Django 5.0, Django REST Framework, SQLite (Dev) / PostgreSQL (Prod) |
| **AI / Intelligence** | Deterministic Multi-Factor Scoring Engines, Canonical Skill Normalization, LLM Integration Ready |
| **Document Processing** | `pypdf`, native `zipfile` & `xml.etree` for Word DOCX, text parser |

---

## 🔌 API Endpoints Reference

### Skill Gap & Career Intelligence
- `GET /api/career/skill-gap/` — Retrieve the student's latest skill gap analysis for their target role.
- `POST /api/career/skill-gap/analyze/` — Trigger a fresh multi-dimensional skill gap evaluation.
- `POST /api/career/target-career/` — Set or update student's target career role.
- `GET /api/career/my-recommendations/` — Get AI career recommendations with transparent factor breakdowns.

### Resume & Skill Sync
- `POST /api/students/resume/analyze/` — Upload PDF/DOCX/TXT resume for ATS evaluation & skill extraction.
- `GET /api/students/resume/latest/` — Retrieve latest resume analysis report.
- `POST /api/students/resume/import-skills/` — Import extracted resume skills directly into the student profile.

### Adaptive Roadmap & Gamification
- `GET /api/learning/roadmap/` — Retrieve active personalized learning roadmap.
- `POST /api/learning/roadmap/generate/` — Generate or regenerate 4-phase adaptive roadmap.
- `POST /api/learning/items/<id>/complete/` — Complete a roadmap task (triggers +15% skill bump, +50 XP, readiness recalculation).
- `GET /api/learning/gamification/` — Get student XP, level, streak, and unlocked badges.
- `POST /api/learning/gamification/daily-checkin/` — Claim daily check-in streak reward.

### AI Learning Chatbot
- `POST /api/chatbot/messages/` — Send query to 360° context-aware AI assistant.
- `GET /api/chatbot/conversations/` — List student conversation history.

---

## 🚀 Quick Start Guide

### Prerequisites
- Python 3.11+
- Node.js 18+ & npm

### 1. Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv
venv\Scripts\activate   # Windows
# source venv/bin/activate # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Seed career intelligence & skills database
python manage.py seed_intelligence

# Start Django development server
python manage.py runserver
```

### 2. Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Start Vite dev server
npm run dev

# Or build for production
npm run build
```

---

## 🧪 Testing & Verification

1. **Backend Verification**:
   ```bash
   python manage.py check
   ```
2. **Seed Verification**:
   Run `python manage.py seed_intelligence` to populate career paths (AI/ML Engineer, Full Stack Developer, Data Scientist, Cloud Architect) and skill requirements.
3. **Frontend Build Verification**:
   ```bash
   npm run build
   ```

---

## 📄 License
This project is licensed under the MIT License.
