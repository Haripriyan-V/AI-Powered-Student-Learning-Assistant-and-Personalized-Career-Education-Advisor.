# DishaAI – AI-Powered Student Learning Assistant & Career Advisor
## Backend (Django REST Framework + MySQL + JWT)

This is the complete backend for DishaAI, built with Django REST Framework,
JWT authentication (SimpleJWT), and MySQL.

## Apps

| App        | Purpose                                                              |
|------------|-----------------------------------------------------------------------|
| `accounts` | Custom User model, registration, login (JWT), profile, password mgmt |
| `students` | Student profiles, education history, skills, interests               |
| `learning` | Subjects, courses, learning resources, quizzes, progress tracking    |
| `career`   | Career fields/paths, aptitude assessments, AI-ready recommendations  |
| `chatbot`  | AI learning-assistant chat sessions & messages                       |

## 1. Setup

```bash
# Create & activate a virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

> `mysqlclient` requires MySQL client dev headers.
> - Ubuntu/Debian: `sudo apt-get install default-libmysqlclient-dev build-essential pkg-config`
> - macOS: `brew install mysql-client pkg-config`
> - Windows: install the prebuilt wheel, or use `pip install mysqlclient` after installing MySQL Connector C.

## 2. Configure environment

Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
```

Create the MySQL database (matching `DB_NAME` in `.env`):

```sql
CREATE DATABASE sih25094_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

## 3. Run migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

## 4. Create a superuser (for /admin/)

```bash
python manage.py createsuperuser
```

## 5. Run the development server

```bash
python manage.py runserver
```

API will be live at `http://127.0.0.1:8000/`, admin at `/admin/`.

## API Overview

### Auth (`/api/accounts/`)
- `POST register/` — create account (role: student/counselor/admin)
- `POST login/` — JWT login (username or email + password) → `{access, refresh, user}`
- `POST token/refresh/` (top-level `/api/auth/token/refresh/`) — refresh access token
- `GET/PATCH profile/` — view/update own profile
- `POST change-password/`
- `POST logout/`

### Students (`/api/students/`)
- `GET/PATCH profile/me/` — current student's profile (auto-created)
- `/profiles/` — counselor/admin read-only listing of all student profiles
- `/education/` — CRUD own education history
- `/my-skills/` — CRUD own skills
- `/interests/`, `/skills/` — catalog (read for all, write for counselor/admin)

### Learning (`/api/learning/`)
- `/subjects/`, `/courses/`, `/resources/` — catalog CRUD (write restricted)
- `POST courses/{id}/enroll/` — start progress tracking
- `/quizzes/`, `/questions/`, `/choices/` — quiz authoring
- `POST quizzes/{id}/submit/` — submit answers, get graded
- `/attempts/` — own (or all, for staff) quiz attempts
- `/progress/` — own (or all, for staff) course progress

### Career (`/api/career/`)
- `/fields/`, `/paths/` — career catalog
- `/tests/` — aptitude assessments
- `POST tests/{id}/submit/` — submit answers → auto-generates recommendations
- `/results/` — own (or all) assessment results
- `/recommendations/`, `GET my-recommendations/` — career recommendations

### Chatbot (`/api/chatbot/`)
- `/sessions/` — own chat sessions
- `POST sessions/{id}/send_message/` — send a message, get AI reply
- `/messages/` — read own messages

## Notes
- JWT auth header: `Authorization: Bearer <access_token>`
- The chatbot's `generate_ai_reply()` (in `chatbot/views.py`) and the career
  recommendation scorer (in `career/views.py`) are intentionally isolated,
  rule-based placeholders — swap them for a real ML/LLM model in the AI
  module phase without touching any other code.
- `DEBUG=True` serves `/media/` and `/static/` directly for convenience.
