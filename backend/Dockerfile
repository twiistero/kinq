FROM python:3.12-slim
WORKDIR /srv
COPY backend/requirements.txt /srv/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/app /srv/app
COPY content /srv/source/content
CMD ["sh", "-c", "python -m app.init_db && uvicorn app.main:app --host 0.0.0.0 --port 8000 --proxy-headers"]
