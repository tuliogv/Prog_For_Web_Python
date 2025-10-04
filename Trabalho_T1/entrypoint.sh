#!/usr/bin/env bash
set -e

# Migrações
python manage.py migrate --noinput

# Cria superusuário se não existir (usa variáveis ou defaults)
PY_SUPERUSER_USERNAME="${DJANGO_SUPERUSER_USERNAME:-admin}"
PY_SUPERUSER_EMAIL="${DJANGO_SUPERUSER_EMAIL:-admin@example.com}"
PY_SUPERUSER_PASSWORD="${DJANGO_SUPERUSER_PASSWORD:-admin123}"

python manage.py shell <<'PYCODE'
from django.contrib.auth import get_user_model
import os
User = get_user_model()
u = os.environ.get("DJANGO_SUPERUSER_USERNAME","admin")
e = os.environ.get("DJANGO_SUPERUSER_EMAIL","admin@example.com")
p = os.environ.get("DJANGO_SUPERUSER_PASSWORD","admin123")
if not User.objects.filter(username=u).exists():
    User.objects.create_superuser(u, e, p)
    print(f"Superuser '{u}' criado.")
else:
    print(f"Superuser '{u}' já existe.")
PYCODE

# Coleta estáticos (se quiser usar em prod com DEBUG=0)
if [ "${DEBUG:-1}" = "0" ]; then
  python manage.py collectstatic --noinput || true
fi

# Sobe o servidor (padrão: runserver pra casar com seu comando)
if [ "${USE_GUNICORN:-0}" = "1" ]; then
  exec gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers ${WORKERS:-2} --timeout ${TIMEOUT:-120}
else
  exec python manage.py runserver 0.0.0.0:8000
fi
