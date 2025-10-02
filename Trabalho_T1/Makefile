# ==== Configurações ====
# Troque pelo seu usuário do Docker Hub se for publicar a imagem
IMAGE ?= tuliogv/minitwitter
TAG ?= latest
PORT ?= 8000
CONTAINER_NAME ?= minitwitter

# Caminhos
VENV := .venv
PY := $(VENV)/bin/python
PIP := $(VENV)/bin/pip

# Arquivos (opcional: mantêm SQLite e mídia fora do container)
DB_FILE := db.sqlite3
MEDIA_DIR := media

# ==== Ajuda ====
.PHONY: help
help:
	@echo "Comandos principais:"
	@echo "  make venv            -> cria o virtualenv local"
	@echo "  make install         -> instala deps no venv"
	@echo "  make migrate         -> migra BD (local)"
	@echo "  make run             -> roda dev server local"
	@echo "  make docker-build    -> builda a imagem Docker ($(IMAGE):$(TAG))"
	@echo "  make docker-run      -> roda o container (porta $(PORT))"
	@echo "  make docker-stop     -> para/remover o container"
	@echo "  make docker-shell    -> abre /bin/bash dentro do container"
	@echo "  make docker-migrate  -> executa 'manage.py migrate' no container"
	@echo "  make docker-super    -> executa 'manage.py createsuperuser' no container"
	@echo "  make docker-logs     -> ver logs do container"
	@echo "  make docker-push     -> faz push da imagem para o Docker Hub"

# ==== Ambiente local (opcional) ====
.PHONY: venv install migrate run
venv:
	python -m venv $(VENV)

install: venv
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt

migrate:
	$(PY) manage.py migrate

run:
	$(PY) manage.py runserver 0.0.0.0:$(PORT)

# ==== Docker ====
.PHONY: docker-build docker-run docker-stop docker-logs docker-shell docker-migrate docker-super docker-push
docker-build:
	docker build -t $(IMAGE):$(TAG) .

# Observação:
# - Monta ./media e ./db.sqlite3 para persistir dados localmente
# - Lê variáveis do arquivo .env se existir (SECRET_KEY, DEBUG, ALLOWED_HOSTS etc.)
docker-run:
	@if [ ! -f $(DB_FILE) ]; then touch $(DB_FILE); fi
	@mkdir -p $(MEDIA_DIR)
	docker run -d --name $(CONTAINER_NAME) \
		--env-file .env \
		-p $(PORT):8000 \
		-v $$PWD/$(MEDIA_DIR):/app/$(MEDIA_DIR) \
		-v $$PWD/$(DB_FILE):/app/$(DB_FILE) \
		$(IMAGE):$(TAG)

docker-stop:
	- docker stop $(CONTAINER_NAME)
	- docker rm $(CONTAINER_NAME)

docker-logs:
	docker logs -f $(CONTAINER_NAME)

docker-shell:
	docker exec -it $(CONTAINER_NAME) /bin/bash

docker-migrate:
	docker exec -it $(CONTAINER_NAME) python manage.py migrate

docker-super:
	docker exec -it $(CONTAINER_NAME) python manage.py createsuperuser

docker-push:
	docker push $(IMAGE):$(TAG)
