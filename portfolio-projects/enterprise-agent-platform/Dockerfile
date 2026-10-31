FROM python:3.12-slim
WORKDIR /srv
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY backend backend
COPY frontend frontend
COPY eval eval
ENV DB_PATH=/srv/runtime/cases.sqlite3
RUN mkdir -p /srv/runtime && useradd -m app && chown -R app:app /srv/runtime
USER app
EXPOSE 8000
CMD ["uvicorn","backend.api:app","--host","0.0.0.0","--port","8000"]
