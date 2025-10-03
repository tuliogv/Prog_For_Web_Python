# MiniTwitter — Django (sem JavaScript)

Projeto acadêmico completo de um microblog (tipo “Twitter”) feito com **Django 5**, **HTML** e **Bootstrap (apenas CSS, via CDN)**.
O objetivo é demonstrar um CRUD completo, autenticação, autorização, MVT do Django e publicação em container, mantendo **zero JavaScript**.

Integrantes do Grupo:
Thiago Henriques
Tulio Gomes

Link para acessar o site: http://3.88.104.254:8000/

---

## Sumário

- [MiniTwitter — Django (sem JavaScript)](#minitwitter--django-sem-javascript)
  - [Sumário](#sumário)
  - [Recursos do projeto](#recursos-do-projeto)
  - [Arquitetura (MVT) e módulos do Django](#arquitetura-mvt-e-módulos-do-django)
    - [Model](#model)
    - [View](#view)
    - [Template](#template)
    - [URLs/Rotas](#urlsrotas)
    - [Forms](#forms)
    - [Autenticação/Autorização](#autenticaçãoautorização)
    - [Arquivos estáticos](#arquivos-estáticos)
    - [Configurações principais](#configurações-principais)
  - [Como executar localmente](#como-executar-localmente)
    - [Pré-requisitos](#pré-requisitos)
    - [Passo a passo](#passo-a-passo)
  - [Como executar com Docker](#como-executar-com-docker)
- [3.1 Build da imagem](#31-build-da-imagem)
- [3.2 Subir o container (em background)](#32-subir-o-container-em-background)
- [3.3 (primeira vez) migrar e criar superusuário dentro do container](#33-primeira-vez-migrar-e-criar-superusuário-dentro-do-container)
  - [Banco de dados](#banco-de-dados)
  - [Operações CRUD implementadas](#operações-crud-implementadas)
  - [Boas práticas de colaboração (GitHub)](#boas-práticas-de-colaboração-github)
  - [Testes rápidos (opcional)](#testes-rápidos-opcional)
  - [Resolução de problemas](#resolução-de-problemas)
- [A) Usando a imagem publicada no Docker Hub (sem código-fonte)](#a-usando-a-imagem-publicada-no-docker-hub-sem-código-fonte)
- [B) Buildar a imagem a partir do código (usando o Makefile)](#b-buildar-a-imagem-a-partir-do-código-usando-o-makefile)
  - [Variáveis que você pode trocar “on the fly”](#variáveis-que-você-pode-trocar-on-the-fly)
  - [Dicas de produção/servidor](#dicas-de-produçãoservidor)
  - [Troubleshooting rápido](#troubleshooting-rápido)
  - [Resumo dos comandos principais](#resumo-dos-comandos-principais)
  - [Licença](#licença)
    - [Anexo: versões das dependências (sugeridas)](#anexo-versões-das-dependências-sugeridas)

---

## Recursos do projeto

* ✅ **Django 5** com padrão **MVT** (Model–View–Template)
* ✅ **CRUD completo** de posts (Create, Read, Update, Delete)
* ✅ **Login/Logout/Registro** de usuário (cadastro simples sem “ajuda” de senha)
* ✅ **Timeline pública (somente leitura)** e **CRUD restrito** (autor ou staff)
* ✅ **Sem JavaScript** — layout responsivo com **Bootstrap (CSS via CDN)**
* ✅ **Controle de acesso**:

  * **Anônimo**: pode ver listas e detalhes
  * **Autenticado**: pode **criar** posts
  * **Autor** ou **staff**: pode **editar/excluir**
* ✅ **Página de login** exibe posts recentes (somente leitura)
* ✅ **Arquivos estáticos** servidos com **WhiteNoise** (no container)
* ✅ **Container** com **Docker + Gunicorn**
* ✅ Pronto para **migrar para Postgres** via `DATABASE_URL` (dj-database-url)
* ✅ README detalhado (este documento)

---

## Arquitetura (MVT) e módulos do Django

**MVT** do Django é a organização nativa do framework:

* **Model** — camada de dados (ORM). Define tabelas e relações.
* **View** — lógica de requisição/resposta (controla o fluxo, busca/valida dados).
* **Template** — camadas de apresentação (HTML + tags Django).
* **URLs** — roteamento que liga paths a views.
* **Forms** — validação/formatação de dados de entrada.
* **Admin** — painel administrativo (opcional, já incluído).
* **Middleware** — camadas transversais (segurança, sessão, CSRF, etc.).
* **Settings** — configuração global do projeto.

Abaixo, como cada módulo é usado aqui:

### Model

**`posts/models.py`** define a entidade principal:

```python
from django.db import models
from django.contrib.auth.models import User

class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    message = models.TextField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.author.username}: {self.message[:30]}"
```

* `author`: relação com `User` (auth nativo do Django)
* `message`: texto do post
* `created_at`/`updated_at`: timestamps automáticos
* `ordering`: timeline do mais novo para o mais antigo

### View

Usamos **class-based views**:

* **ListView** — lista de posts (pública)
* **DetailView** — detalhe de post (pública)
* **CreateView** — criar (apenas autenticados)
* **UpdateView** / **DeleteView** — editar/excluir (autor ou staff)
* **LoginView customizada** — adiciona posts recentes no contexto
* **FormView** — registro de usuários

Trecho principal (resumo):

```python
class PostListView(ListView): ...
class PostDetailView(DetailView): ...
class PostCreateView(LoginRequiredMixin, CreateView): ...
class OwnerOrStaffRequiredMixin(UserPassesTestMixin): ...
class PostUpdateView(LoginRequiredMixin, OwnerOrStaffRequiredMixin, UpdateView): ...
class PostDeleteView(LoginRequiredMixin, OwnerOrStaffRequiredMixin, DeleteView): ...

class PublicLoginView(LoginView):
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["recent_posts"] = Post.objects.select_related("author").all()[:10]
        return ctx

class SignUpView(FormView): ...
```

### Template

* Páginas herdando de `base.html` com **Bootstrap (CSS)** via CDN.
* **Sem JS**: todos os componentes são classes utilitárias (`container`, `row`, `card`, `btn`, `m-1`, `p-4`, etc.).
* Uso do `{% cycle %}` para alternar **fundos leves** nos cards.
* **Tags de template** comuns: `{% url %}`, `{% csrf_token %}`, filtros como `|date` e `|linebreaksbr`.

### URLs/Rotas

**`config/urls.py`** (resumo):

```python
urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/login/", PublicLoginView.as_view(), name="login"),
    path("accounts/logout/", LogoutView.as_view(), name="logout"),
    path("accounts/signup/", SignUpView.as_view(), name="signup"),
    path("", include("posts.urls")),
]
```

**`posts/urls.py`**:

```python
urlpatterns = [
    path("", PostListView.as_view(), name="list"),          # público
    path("<int:pk>/", PostDetailView.as_view(), name="detail"),
    path("novo/", PostCreateView.as_view(), name="create"),  # autenticado
    path("<int:pk>/editar/", PostUpdateView.as_view(), name="update"),
    path("<int:pk>/excluir/", PostDeleteView.as_view(), name="delete"),
]
```

### Forms

* **`PostForm`** — formulário de post (message)
* **`SignUpForm`** — cadastro de usuário **sem help\_text** chato; usa `UserCreationForm` como base, mas limpa os textos.

### Autenticação/Autorização

* **Login/Logout**: views nativas (`LoginView`, `LogoutView`); **logout via POST** (boa prática).
* **Registro**: `SignUpView` (cria usuário).
* **Permissões**:

  * Qualquer pessoa **lê** (`ListView`, `DetailView` não exigem login).
  * **Criar**: apenas autenticados.
  * **Editar/Excluir**: autor do post ou usuário staff (mixins na view).
* **Redirecionamentos**:

  * `LOGIN_REDIRECT_URL = "posts:list"`
  * `LOGOUT_REDIRECT_URL = "login"`

### Arquivos estáticos

* **Bootstrap CSS** por **CDN** (somente `<link>` do CSS).
* WhiteNoise configurado para **`collectstatic`** e servir **estáticos** no container.
* Se mantiver um CSS adicional (opcional), coloque-o em `static/css/` e referencie com `{% static %}` após `{% load static %}` no `base.html`.

**Link recomendado do Bootstrap (CSS, sem JS):**

```html
<link
  href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.8/dist/css/bootstrap.min.css"
  rel="stylesheet"
  integrity="sha384-sRIl4kxILFvY47J16cr9ZwB07vP4J8+LH7qKQnuqkuIAvNWLzeN8tE5YBujZqJLB"
  crossorigin="anonymous"
/>
```

> Se trocar a **versão**, troque também o **SRI (`integrity`)** correspondente; caso contrário, o navegador bloqueará o CSS.

### Configurações principais

**`config/settings.py`** (pontos de atenção):

* **Segurança / Ambiente**

  * `SECRET_KEY` (use variável de ambiente em produção)
  * `DEBUG` (0/1)
  * `ALLOWED_HOSTS` (em dev pode ser `"*"`; em produção, especifique os domínios)
  * `CSRF_TRUSTED_ORIGINS` (adicione `https://<seu-dominio>` quando publicar)

* **Banco de dados**

  * SQLite por padrão
  * Se `DATABASE_URL` (ex.: Postgres), o `dj-database-url` assume.

* **Estáticos**

  * `STATIC_URL`, `STATIC_ROOT`, `STATICFILES_DIRS`
  * `WhiteNoiseMiddleware` e `CompressedManifestStaticFilesStorage`

* **Senha**

  * `AUTH_PASSWORD_VALIDATORS = []` (neste projeto, sem validações “chatas” — ajuste conforme necessidade)

* **Proxy TLS (Codespaces/PaaS)**

  * `SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")`

## Como executar localmente

### Pré-requisitos

* **Python 3.12+**
* (Opcional) **Git** e **virtualenv** (ou `venv`)
* (Opcional) Docker

### Passo a passo

1. **Clone o repositório** e entre na pasta do projeto (raiz do Django):

```bash
git clone <URL-do-seu-repo>.git
cd Trabalho_T1
```

2. **Crie e ative o ambiente virtual**:

```bash
python -m venv .venv
# Linux/macOS
source .venv/bin/activate
# Windows PowerShell
# .venv\Scripts\Activate.ps1
```

3. **Instale as dependências**:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

4. **Configuração opcional de ambiente** (arquivo `.env` ou variáveis):

* `SECRET_KEY="sua-secret"` (produção)
* `DEBUG=1` (dev) / `0` (prod)
* `ALLOWED_HOSTS="localhost,127.0.0.1"`
* `DATABASE_URL="postgres://user:pass@host:5432/dbname"` (se usar Postgres)

5. **Aplique migrações** e **crie um superusuário**:

```bash
python manage.py migrate
python manage.py createsuperuser
```

6. **(Opcional) Coletar estáticos** para testar com WhiteNoise:

```bash
python manage.py collectstatic --noinput
```

7. **Execute o servidor**:

```bash
python manage.py runserver 0.0.0.0:8000
```

8. **Acesse**:

* App: `http://127.0.0.1:8000/`
* Login: `http://127.0.0.1:8000/accounts/login/`
* Admin: `http://127.0.0.1:8000/admin/`

> **Codespaces/Proxies**: se usar `https://<codespace>-8000.app.github.dev`, inclua esse domínio em `CSRF_TRUSTED_ORIGINS` e `ALLOWED_HOSTS`.

---

## Como executar com Docker

>> 
# 3.1 Build da imagem
make docker-build

# 3.2 Subir o container (em background)
make docker-run

# 3.3 (primeira vez) migrar e criar superusuário dentro do container
make docker-migrate
make docker-super
>>


## Banco de dados

* **Padrão: SQLite** (arquivo `db.sqlite3` na raiz).
* **Produção**: recomenda-se **PostgreSQL** (RDS/Cloud SQL/Azure DB).
* **Troca automática** via `DATABASE_URL` (lib `dj-database-url`).

Exemplo de `DATABASE_URL`:

```
postgres://usuario:senha@host:5432/nomedb
```

---

## Operações CRUD implementadas

* **Create**: `POST /novo/` (form HTML)
* **Read**:

  * `GET /` (lista pública, paginação)
  * `GET /<id>/` (detalhe público)
* **Update**: `POST /<id>/editar/` (autor/staff)
* **Delete**: `POST /<id>/excluir/` (autor/staff)

**Regras de UI (templates):**

* Botões **Editar/Excluir** só aparecem se `user.is_staff` **ou** `user.id == p.author_id`.
* **Logout** é **POST** com `{% csrf_token %}` (segurança).

---

## Boas práticas de colaboração (GitHub)

* Branch por funcionalidade: `feat/nome`, `fix/issue-123`, etc.
* Pull Requests com revisão entre colegas.
* Commits pequenos e descritivos.
* `db.sqlite3` e `.env` **não** devem ir para o Git (estão no `.gitignore`).
* Releases/Tags para marcos do projeto.

---

## Testes rápidos (opcional)

Instale `pytest` e `pytest-django` (opcional):

```bash
pip install pytest pytest-django
```

Crie `pytest.ini`:

```ini
[pytest]
DJANGO_SETTINGS_MODULE = config.settings
python_files = tests.py test_*.py *_tests.py
```

Exemplo mínimo de teste em `posts/tests/test_models.py`:

```python
import pytest
from django.contrib.auth.models import User
from posts.models import Post

@pytest.mark.django_db
def test_post_str():
    u = User.objects.create(username="alice")
    p = Post.objects.create(author=u, message="olá mundo")
    assert "alice" in str(p)
```

Rode:

```bash
pytest -q
```

---

## Resolução de problemas

* **Bootstrap não aplica estilo**

  * Verifique o `<link>` do CDN e o **SRI `integrity` correspondente** à versão.
  * Faça *hard reload* ou limpe o cache.

* **Erro de CSRF (403) com domínio externo (Codespaces/PaaS)**

  * Adicione o domínio em `CSRF_TRUSTED_ORIGINS` (com esquema `https://`).
  * Confira `ALLOWED_HOSTS`.
  * Se estiver atrás de proxy TLS, mantenha `SECURE_PROXY_SSL_HEADER`.

* **Logout não funciona**

  * Logout deve ser **POST** para `/accounts/logout/` com `{% csrf_token %}`.
  * `LOGOUT_REDIRECT_URL = "login"`.

* **Parênteses em `{% if %}`** (TemplateSyntaxError)

  * Não use parênteses em expressões complexas; separe com `if` aninhados:

    ```django
    {% if user.is_authenticated %}
      {% if user.is_staff or user.id == p.author_id %}
        ...
      {% endif %}
    {% endif %}
    ```

* **Validações de senha “chatas”**

  * Neste projeto estão desativadas com `AUTH_PASSWORD_VALIDATORS = []`.
  * Para reativar, use os validadores padrão do Django.

---

Perfeito — com **esse Makefile** você consegue **buildar, rodar, migrar e criar o admin** do seu Django em qualquer máquina com Docker. Abaixo está o **passo a passo completo**, cobrindo dois cenários:

* **A)** Rodar **baixando a imagem do Docker Hub** (sem precisar do código-fonte)
* **B)** Rodar **buildando a imagem a partir do código** (usando o mesmo Makefile)

> Pré-requisitos na máquina alvo:
>
> * Docker instalado (Linux/macOS/Windows).
> * (Opcional) Conta no Docker Hub para `docker login` (se for **puxar** ou **publicar** a imagem).
> * Porta **8000** liberada no firewall (ou use outra com `PORT=...`).
> * Em Linux, talvez precise usar `sudo docker ...` (ou adicione seu usuário ao grupo `docker`).

---

# A) Usando a imagem publicada no Docker Hub (sem código-fonte)

1. **Tenha o Makefile e um `.env`** na mesma pasta (pode ser uma pasta vazia sua).

   * Salve o Makefile que você enviou (ajuste `IMAGE`, `TAG`, `PORT` se quiser).
   * Crie um **`.env`** com variáveis mínimas:

     ```env
     SECRET_KEY=troque-por-uma-chave-forte
     DEBUG=0
     # Se for acessar de outra máquina/domínio, inclua aqui
     ALLOWED_HOSTS=localhost,127.0.0.1
     CSRF_TRUSTED_ORIGINS=http://localhost,http://127.0.0.1
     # Banco padrão: SQLite dentro do container (vamos montar um volume para persistir)
     # Se futuramente usar Postgres: DATABASE_URL=postgres://user:pass@host:5432/dbname
     ```

     > Se for expor por HTTPS/ domínio, inclua o domínio/IP aqui também:
     > `ALLOWED_HOSTS=seu-dominio.com,SEU.IP.AQUI`
     > `CSRF_TRUSTED_ORIGINS=https://seu-dominio.com`

2. **Login no Docker Hub** (se a imagem for privada ou se você quiser publicar depois):

   ```bash
   docker login
   ```

3. **Rodar o container (pull automático se necessário)**

   ```bash
   make docker-run IMAGE=tuliogv/minitwitter TAG=latest PORT=8000
   ```

   O Makefile:

   * Cria `db.sqlite3` e `media/` locais (se não existirem).
   * Mapeia `db.sqlite3` e `media/` para dentro do container (dados persistem fora).
   * Passa as variáveis do `.env` com `--env-file .env`.

4. **Aplicar migrações e criar o admin**:

   ```bash
   make docker-migrate CONTAINER_NAME=minitwitter
   make docker-super   CONTAINER_NAME=minitwitter
   ```

   > O `CONTAINER_NAME` padrão no Makefile já é `minitwitter`. Só passe se você tiver alterado.

5. **Acessar a aplicação**

   * Local: [http://localhost:8000](http://localhost:8000)
   * Em servidor remoto: use `http://SEU.IP:8000` (ou configure um proxy HTTPS e ajuste `ALLOWED_HOSTS`/`CSRF_TRUSTED_ORIGINS` no `.env`).

6. **Operações úteis**

   ```bash
   make docker-logs        # ver logs ao vivo
   make docker-shell       # entrar no /bin/bash do container
   make docker-stop        # parar/remover o container
   ```

> Quer publicar a **mesma imagem** (se você tiver o push permitido)?
>
> ```bash
> make docker-push IMAGE=tuliogv/minitwitter TAG=latest
> ```

---

# B) Buildar a imagem a partir do código (usando o Makefile)

1. **Obter o projeto (com Dockerfile e Makefile na raiz)**

   ```bash
   git clone <seu-repo>.git
   cd <seu-repo>
   ```

   Certifique-se de que:

   * `manage.py` está na **raiz** do repositório.
   * O projeto Django está em `Trabalho_T1/` com `config/`, `posts/`, `templates/`, `static/`, `requirements.txt`.
   * `Dockerfile` aponta o WSGI correto e exporta `PYTHONPATH`:

     * `gunicorn Trabalho_T1.config.wsgi:application`
     * `ENV PYTHONPATH=/app/Trabalho_T1:/app`
     * `WORKDIR /app`
     * `ENTRYPOINT`/`CMD` (no seu `entrypoint.sh`) executa `migrate` + `collectstatic` + `gunicorn`.

2. **Criar `.env` na raiz** (igual ao cenário A):

   ```env
   SECRET_KEY=troque-por-uma-chave-forte
   DEBUG=0
   ALLOWED_HOSTS=localhost,127.0.0.1
   CSRF_TRUSTED_ORIGINS=http://localhost,http://127.0.0.1
   ```

3. **Buildar a imagem**

   ```bash
   make docker-build IMAGE=tuliogv/minitwitter TAG=latest
   ```

4. **Subir o container**

   ```bash
   make docker-run IMAGE=tuliogv/minitwitter TAG=latest PORT=8000
   ```

5. **Migrar e criar superusuário**

   ```bash
   make docker-migrate
   make docker-super
   ```

6. **Acessar**

   * [http://localhost:8000](http://localhost:8000)

7. **(Opcional) Publicar no Docker Hub**

   ```bash
   docker login
   make docker-push IMAGE=tuliogv/minitwitter TAG=latest
   ```

---

## Variáveis que você pode trocar “on the fly”

Todos os alvos do Makefile aceitam overrides:

```bash
make docker-build IMAGE=seunome/minitwitter TAG=v1
make docker-run   IMAGE=seunome/minitwitter TAG=v1 PORT=8080 CONTAINER_NAME=miniweb
make docker-migrate CONTAINER_NAME=miniweb
```

---

## Dicas de produção/servidor

* **Firewall**: libere a porta que você escolher (8000 ou outra).
* **Domínio/HTTPS** (recomendado):

  * Use um proxy reverso (Caddy, Traefik, Nginx Proxy Manager) na frente do container.
  * Ajuste o `.env`:

    ```
    ALLOWED_HOSTS=seu-dominio.com
    CSRF_TRUSTED_ORIGINS=https://seu-dominio.com
    DEBUG=0
    ```
* **Usuários & uploads**:

  * Os uploads ficam montados em `./media` (no host).
  * O SQLite (se mantido) está em `./db.sqlite3` (no host).
  * Para escalar, troque para Postgres (defina `DATABASE_URL` no `.env`).

---

## Troubleshooting rápido

* **`docker compose ps` vazio / container cai** → veja logs:

  ```bash
  make docker-logs
  ```

  Erros comuns e correções:

  * `ModuleNotFoundError: posts` → garanta que a imagem exporta `PYTHONPATH=/app/Trabalho_T1:/app` e que o `manage.py` está na raiz.
  * **CSRF 403** ao enviar formulários → confira `{% csrf_token %}` em todos os `<form method="post">` e ajuste `CSRF_TRUSTED_ORIGINS` no `.env`.
  * **401 no Codespaces** → porta não está **Public** na aba **PORTS**.

* **Mudar de porta**:

  ```bash
  make docker-stop
  make docker-run PORT=8080
  ```

---

## Resumo dos comandos principais

```bash
# BAIXANDO A IMAGEM DO HUB (sem código)
make docker-run IMAGE=tuliogv/minitwitter TAG=latest PORT=8000
make docker-migrate
make docker-super

# OU, BUILDANDO DA FONTE
make docker-build IMAGE=tuliogv/minitwitter TAG=latest
make docker-run   IMAGE=tuliogv/minitwitter TAG=latest PORT=8000
make docker-migrate
make docker-super

# Logs / shell / parar
make docker-logs
make docker-shell
make docker-stop
```

Se quiser, te entrego um **`.env.example`** e um **README.md** prontinhos (com essas instruções) para você só copiar pro repositório. Quer?

---

## Licença

Uso acadêmico/educacional. Sinta-se à vontade para adaptar e publicar melhorias.

---

### Anexo: versões das dependências (sugeridas)

`requirements.txt`:

```
Django==5.0.7
gunicorn==22.0.0
whitenoise==6.7.0
dj-database-url==2.2.0
python-dotenv==1.0.1
```

> Caso utilize Docker: o `Dockerfile` já executa `collectstatic` e inicia `gunicorn`. Ajuste variáveis de ambiente no `docker run` ou no PaaS.
