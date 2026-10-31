FROM python:3.12-slim
WORKDIR /srv
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY core core
COPY backend backend
COPY frontend frontend
COPY scripts scripts
ENV ARTIFACTS_DIR=/srv/artifacts
RUN mkdir -p /srv/artifacts && useradd -m app && chown -R app:app /srv/artifacts
USER app
EXPOSE 8001
CMD ["uvicorn","backend.api:app","--host","0.0.0.0","--port","8001"]
