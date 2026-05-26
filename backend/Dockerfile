# ============================================================
# mada_fisc_auto — Dockerfile multi-stage backend
# ============================================================

# --- Stage 1: Builder — installation des dépendances ---
FROM python:3.12-slim AS builder

# Dépendances système pour WeasyPrint
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /build

# Copier les requirements et installer dans un virtualenv
COPY requirements/ requirements/
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir -r requirements/base.txt


# --- Stage 2: Development ---
FROM python:3.12-slim AS development

# Dépendances runtime pour WeasyPrint
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf-2.0-0 \
    libffi-dev \
    libcairo2 \
    fonts-noto \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copier le virtualenv du builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Installer les dépendances de dev
COPY requirements/ requirements/
RUN pip install --no-cache-dir -r requirements/dev.txt

# Copier le code source
COPY . .

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]


# --- Stage 3: Production ---
FROM python:3.12-slim AS production

# Dépendances runtime minimales
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf-2.0-0 \
    libffi-dev \
    libcairo2 \
    fonts-noto \
    && rm -rf /var/lib/apt/lists/*

# Utilisateur non-root pour la sécurité
RUN groupadd -r mada && useradd -r -g mada mada

WORKDIR /app

# Copier le virtualenv du builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copier le code source
COPY . .

# Répertoires pour les fichiers statiques et médias
RUN mkdir -p /app/staticfiles /app/media && chown -R mada:mada /app

USER mada

EXPOSE 8000

CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "4", "--timeout", "120"]
