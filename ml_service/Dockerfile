FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

COPY requirements.runtime.txt .

RUN --mount=type=cache,target=/root/.cache/pip python -m pip install --timeout 120 --retries 5 -r requirements.runtime.txt

COPY app ./app

EXPOSE 8001

CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]
