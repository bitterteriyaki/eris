# This Dockerfile uses multi-stage build to customize DEV and PROD images:
# https://docs.docker.com/develop/develop-images/multistage-build/

FROM python:3.12.1-slim-buster AS development_build

ARG BOT_ENV \
  UID=1000 \
  GID=1000

ENV BOT_ENV=${BOT_ENV} \
  # Python:
  PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONHASHSEED=random \
  PYTHONDONTWRITEBYTECODE=1 \
  # Pip:
  PIP_NO_CACHE_DIR=1 \
  PIP_DISABLE_PIP_VERSION_CHECK=1 \
  PIP_DEFAULT_TIMEOUT=100 \
  # Poetry:
  POETRY_VERSION=1.7.1 \
  POETRY_NO_INTERACTION=1 \
  POETRY_VIRTUALENVS_CREATE=false \
  POETRY_CACHE_DIR='/var/cache/pypoetry' \
  POETRY_HOME='/usr/local' \
  # Tini
  TINI_VERSION=v0.19.0 \
  # Dockerize:
  DOCKERIZE_VERSION=v0.7.0

SHELL ["/bin/bash", "-eo", "pipefail", "-c"]

RUN apt-get update && apt-get upgrade -y \
  && apt-get install --no-install-recommends -y \
    bash \
    brotli \
    build-essential \
    curl \
    gettext \
    git \
    libpq-dev \
  # Installing Poetry:
  && curl -sSL 'https://install.python-poetry.org' | python - \
  && poetry --version \
  # Installing Dockerize:
  && curl -sSLO "https://github.com/jwilder/dockerize/releases/download/${DOCKERIZE_VERSION}/dockerize-linux-amd64-${DOCKERIZE_VERSION}.tar.gz" \
  && tar -C /usr/local/bin -xzvf "dockerize-linux-amd64-${DOCKERIZE_VERSION}.tar.gz" \
  && rm "dockerize-linux-amd64-${DOCKERIZE_VERSION}.tar.gz" \
  && dockerize --version \
  # installing Tini:
  && dpkgArch="$(dpkg --print-architecture | awk -F- '{ print $NF }')" \
  && curl -o /usr/local/bin/tini -sSLO "https://github.com/krallin/tini/releases/download/${TINI_VERSION}/tini-${dpkgArch}" \
  && chmod +x /usr/local/bin/tini \
  && tini --version \
  # Cleaning cache:
  && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
  && apt-get clean -y && rm -rf /var/lib/apt/lists/*

WORKDIR /bot

RUN groupadd -g "${GID}" -r bot \
  && useradd -d '/bot' -g bot -l -r -u "${UID}" bot \
  && chown bot:bot -R '/bot'

# Copy only requirements, to cache them in Docker layer.
COPY --chown=bot:bot ./poetry.lock ./pyproject.toml /bot/

# Project initialization:
RUN --mount=type=cache,target="$POETRY_CACHE_DIR" \
  echo "$BOT_ENV" \
  && poetry version \
  && poetry run pip install -U pip \
  && poetry install \
    $(if [ "$BOT_ENV" = 'production' ]; then echo '--only main'; fi) \
    --no-interaction --no-ansi

# Running as non-root user:
USER bot


FROM development_build AS production_build

COPY --chown=bot:bot . /bot/
