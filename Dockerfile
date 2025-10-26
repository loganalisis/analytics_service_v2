FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip3 install -r requirements.txt

COPY . .

# Load environment variables automatically if .env exists
CMD ["bash", "-c", "python manage.py migrate --noinput && python manage.py runserver 0.0.0.0:8001"]
