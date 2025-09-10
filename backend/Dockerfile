# backend/Dockerfile
FROM python:3.11-slim-bookworm

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV DJANGO_SETTINGS_MODULE=djangocore.settings
ENV DJANGO_SECRET_KEY=build-key-only

# RUN python manage.py migrate --noinput && python manage.py collectstatic --noinput
# RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["sh", "-c", "python manage.py collectstatic --noinput && python manage.py migrate --noinput && gunicorn djangocore.wsgi:application --bind 0.0.0.0:8000"]