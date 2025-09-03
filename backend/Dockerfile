# backend/Dockerfile
FROM python:3.11-slim-bookworm

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV DJANGO_SETTINGS_MODULE=djangocore.settings

RUN python manage.py migrate --noinput && python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["gunicorn", "djangocore.wsgi:application", "--bind", "0.0.0.0:8000"]