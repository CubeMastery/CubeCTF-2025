FROM python:3.9-slim

WORKDIR /app

RUN mkdir -p db

COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 3000

ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV FLASK_RUN_HOST=0.0.0.0 
ENV FLASK_RUN_PORT=3000
ENV PYTHONUNBUFFERED=1

CMD ["python", "run.py"]