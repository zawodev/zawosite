# Backend Django

## Konfiguracja środowiska

1. Skopiuj plik `.env.example` do `.env` i uzupełnij kluczami Google/Facebook.
2. Upewnij się, że masz zainstalowane wymagane pakiety (`pip install -r requirements.txt`).
3. Uruchom migracje: `python manage.py migrate`
4. Stwórz superużytkownika: `python manage.py createsuperuser`
5. Uruchom serwer: `python manage.py runserver`

## SSO
- Google i Facebook wymagają podania kluczy w `.env`.

## Wersjonowanie API i dokumentacja
- Wersjonowanie API odbywa się przez ścieżki URL (np. `/api/v1/`).
- **Nie używaj** `NamespaceVersioning` w DRF, jeśli chcesz mieć automatyczną dokumentację przez drf-spectacular.
- Automatyczna dokumentacja dostępna jest pod:
  - Swagger UI: [http://localhost:8000/api/docs/](http://localhost:8000/api/docs/)
  - Redoc: [http://localhost:8000/api/redoc/](http://localhost:8000/api/redoc/)
  - OpenAPI JSON: [http://localhost:8000/api/schema/](http://localhost:8000/api/schema/)
- Jeśli endpointy nie pojawiają się w dokumentacji, sprawdź czy nie masz włączonego `DEFAULT_VERSIONING_CLASS` w `REST_FRAMEWORK`.