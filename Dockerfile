FROM python:3.11-slim as base

RUN mkdir -p /app
WORKDIR /app

RUN useradd --create-home appuser && chown appuser /app


FROM base as poetry-deps

ARG POETRY_VERSION=1.6.1

ENV LANG=C.UTF-8 \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \

    PIP_NO_CACHE_DIR=off \

    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1

USER appuser
RUN pip install --user pipx
ENV PATH=/home/appuser/.local/bin:$PATH
RUN pipx install poetry==${POETRY_VERSION}

COPY pyproject.toml poetry.lock ./
RUN poetry install --only=main --no-root --no-cache
# now we've installed all the required python deps to /app/.venv


FROM base as runner

ARG UWSGI_VERSION=2.0.22

# uwsgi install, adapted from https://github.com/docker-library/python
RUN set -ex \
    && buildDeps=' \
        gcc \
        libbz2-dev \
        libc6-dev \
        libgdbm-dev \
        liblzma-dev \
        libncurses-dev \
        libreadline-dev \
        libsqlite3-dev \
        libssl-dev \
        libpcre3-dev \
        make \
        tcl-dev \
        tk-dev \
        wget \
        xz-utils \
        zlib1g-dev \
    ' \
    && deps=' \
        libexpat1 \
        libpcre3 \
    ' \
    && apt-get update && apt-get install -y $buildDeps $deps --no-install-recommends  && rm -rf /var/lib/apt/lists/* \
    && pip install uwsgi==${UWSGI_VERSION} \
    && apt-get purge -y --auto-remove $buildDeps \
    && find /usr/local -depth \
    \( \
        \( -type d -a -name test -o -name tests \) \
        -o \
        \( -type f -a -name '*.pyc' -o -name '*.pyo' \) \
    \) -exec rm -rf '{}' +

USER appuser
COPY --from=poetry-deps --chown=appuser /app/.venv /app/.venv
COPY --chown=appuser . .

ENV PYTHONPATH=/app/src:$PYTHONPATH \
    
    UWSGI_WSGI_FILE=src/app.py \
    UWSGI_VIRTUALENV=/app/.venv \

    UWSGI_HTTP=0.0.0.0:35601 \
    UWSGI_WORKERS=1 \
    UWSGI_THREADS=4 \
    UWSGI_MASTER=1 \
    UWSGI_LAZY_APPS=1 \
    UWSGI_WSGI_ENV_BEHAVIOR=holy

ENTRYPOINT ["uwsgi", "--show-config"]
