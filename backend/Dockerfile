FROM python:3.10-slim AS base


USER root
RUN apt-get update && apt-get install -y build-essential curl && rm -rf /var/lib/apt/lists/*


RUN useradd --create-home appuser
WORKDIR /home/appuser
USER appuser


COPY --chown=appuser:appuser requirements.txt ./

USER root
RUN pip install --no-cache-dir --default-timeout=300 \
    --find-links=wheelhouse \
    --extra-index-url https://pypi.org/simple \
    -r requirements.txt



USER appuser


COPY --chown=appuser:appuser . .

EXPOSE 8000


CMD ["python", "-m", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
