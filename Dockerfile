FROM python:3.7-slim

# uwsgi, adapted from https://github.com/docker-library/python.git
# in file python/3.6/slim/Dockerfile
# here for build perf optimization
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
        curl \
    ' \
    && apt-get update && apt-get install -y $buildDeps $deps --no-install-recommends  && rm -rf /var/lib/apt/lists/* \
    && pip install uwsgi \
    && apt-get purge -y --auto-remove $buildDeps \
    && find /usr/local -depth \
    \( \
        \( -type d -a -name test -o -name tests \) \
        -o \
        \( -type f -a -name '*.pyc' -o -name '*.pyo' \) \
    \) -exec rm -rf '{}' +

# Integrating poetry, https://stackoverflow.com/a/69094575/8682376
RUN pip install "poetry==1.2.0"
ENV PATH "$PATH:/root/.local/bin/"

RUN mkdir /var/dock
WORKDIR /var/dock
COPY pyproject.toml poetry.lock ./
# Install packages to system interpreter
RUN poetry config virtualenvs.create false
RUN poetry install --no-interaction

RUN useradd --no-log-init -r appuser
RUN chown appuser .
USER appuser

COPY --chown=appuser . .
RUN ls -lah

ENV PYTHONPATH=src
ENV UWSGI_WSGI_FILE=src/app.py

ENV UWSGI_HTTP=0.0.0.0:35601 UWSGI_MASTER=1
ENV UWSGI_LAZY_APPS=1 UWSGI_WSGI_ENV_BEHAVIOR=holy

# Number of uWSGI workers and threads per worker (customize as needed):
ENV UWSGI_WORKERS=1 UWSGI_THREADS=4

# Start uWSGI
ENTRYPOINT ["uwsgi", "--show-config"]
