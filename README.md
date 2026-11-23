# Tone Neuron 

Tone Neuron is an AI-powered communication coaching platform designed to help users improve their communication skills through interactive experiences and personalized feedback.

## Project Overview

The project is being developed using a modular architecture with a Python backend, PostgreSQL database, Redis caching, and a React-based frontend.

## Technology Stack

### Backend
- Python
- FastAPI
- SQLAlchemy
- Alembic
- PostgreSQL
- Redis
- JWT Authentication

### Frontend
- React
- JavaScript
- CSS

### Desktop
- PySide6

### Infrastructure
- Docker
- Git and GitHub

## Implemented Backend Features

- User registration
- Email OTP verification
- Password reset
- JWT access tokens
- Refresh-token rotation
- Refresh-token reuse detection
- Session management
- Logout and logout-all
- IP-based rate limiting
- Redis-backed failed-login protection
- PostgreSQL security event logging

## Project Structure

```text
TONE_NUERON/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── database/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   └── main.py
│   ├── alembic/
│   └── tests/
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## Local Setup

### 1. Clone the repository

```bash
git clone <repository-url>
cd TONE_NUERON
```

### 2. Create a virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
python -m pip install -r requirements.txt
```

### 4. Configure environment variables

Copy `.env.example` to `.env` and replace the placeholder values.

### 5. Start PostgreSQL and Redis

Start the existing Docker services configured for this project.

### 6. Apply database migrations

```powershell
python -m alembic upgrade head
```

### 7. Start FastAPI

```powershell
python -m uvicorn backend.app.main:app --reload --port 8000
```

## API Documentation

Once the backend is running, open the FastAPI Swagger UI at:

`http://127.0.0.1:8000/docs`

## Development Status

Tone Neuron is under active development.

The authentication infrastructure and security audit foundation are implemented. AI coaching functionality and frontend integration are being developed.

## Security

Sensitive credentials are stored in environment variables and excluded from version control.

The backend includes session revocation, refresh-token rotation, rate limiting, and security event logging.

## License

No license has been selected yet.