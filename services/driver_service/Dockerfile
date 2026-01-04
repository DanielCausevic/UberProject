FROM python:3.12-slim

WORKDIR /app

COPY services/driver_service/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY services/driver_service/ ./
COPY shared ./shared

ENV PYTHONUNBUFFERED=1
EXPOSE 3002

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "3002"]
