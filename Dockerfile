FROM python:3.14-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements.txt .

COPY wheelhouse /tmp/wheelhouse

RUN --mount=type=cache,target=/root/.cache/pip python -m pip install --no-deps /tmp/wheelhouse/*.whl

RUN --mount=type=cache,target=/root/.cache/pip python -m pip install --timeout 120 --retries 5 -r requirements.txt

COPY backend ./backend
COPY alembic.ini .

EXPOSE 8000

CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
