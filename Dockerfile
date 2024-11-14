# Ashley : A self-hosted alternative discussion forum for OpenEdx
#
# Nota bene:
#
# this container expects two volumes for statics and media files (that will be
# served by nginx):
#
# * /data/media
# * /data/static
#
# Once mounted, you will need to collect static files via the eponym django
# admin command:
#
#     python sandbox/manage.py collectstatic
#

# -- Base image --
FROM python:3.8-slim AS base

# Upgrade pip to its latest release to speed up dependencies installation
RUN pip install --upgrade pip

# ---- Front-end builder image ----
FROM node:16 AS front-builder

# Copy frontend app sources
COPY ./src/frontend /builder/src/frontend

WORKDIR /builder/src/frontend

RUN yarn install --frozen-lockfile && \
    yarn compile-translations && \
    yarn build-production && \
    yarn sass-production && \
    yarn webfonts

# ---- Back-end builder image ----
FROM base AS back-builder

WORKDIR /builder

# Copy required python dependencies
COPY setup.py setup.cfg MANIFEST.in /builder/
COPY ./src/ashley /builder/src/ashley/

# Copy distributed application's statics
COPY --from=front-builder \
    /builder/src/ashley/static/ashley/js \
    /builder/src/ashley/static/ashley/js
COPY --from=front-builder \
    /builder/src/ashley/static/ashley/css/main.css \
    /builder/src/ashley/static/ashley/css/main.css
COPY --from=front-builder \
    /builder/src/ashley/static/ashley/font/* \
    /builder/src/ashley/static/ashley/font/
COPY --from=front-builder \
    /builder/src/ashley/static/ashley/css/fonts/* \
    /builder/src/ashley/static/ashley/css/fonts/

RUN mkdir /install && \
    pip install --prefix=/install .[sandbox]

# ---- Core application image ----
FROM base AS core

# Install gettext
RUN apt-get update && \
    apt-get install -y \
    gettext && \
    rm -rf /var/lib/apt/lists/*

# Copy installed python dependencies
COPY --from=back-builder /install /usr/local

# Copy runtime-required files
COPY ./sandbox /app/sandbox
COPY ./upgrades /app/upgrades
COPY ./docker/files/usr/local/bin/entrypoint /usr/local/bin/entrypoint

# Gunicorn
RUN mkdir -p /usr/local/etc/gunicorn
COPY docker/files/usr/local/etc/gunicorn/ashley.py /usr/local/etc/gunicorn/ashley.py

# Give the "root" group the same permissions as the "root" user on /etc/passwd
# to allow a user belonging to the root group to add new users; typically the
# docker user (see entrypoint).
RUN chmod g=u /etc/passwd

# Un-privileged user running the application
ARG DOCKER_USER
USER ${DOCKER_USER}

# We wrap commands run in this container by the following entrypoint that
# creates a user on-the-fly with the container user ID (see USER) and root group
# ID.
ENTRYPOINT [ "/usr/local/bin/entrypoint" ]

# ---- Development image ----
FROM core AS development

ENV PYTHONUNBUFFERED=1

# Switch back to the root user to install development dependencies
USER root:root

WORKDIR /app

# Copy all sources, not only runtime-required files
COPY . /app/

# Uninstall ashley and re-install it in editable mode along with development
# dependencies
RUN pip uninstall -y ashley
RUN pip install -e .[dev]

# Restore the un-privileged user running the application
ARG DOCKER_USER
USER ${DOCKER_USER}

# Target database host (e.g. database engine following docker-compose services
# name) & port
ENV DB_HOST=postgresql \
    DB_PORT=5432

# Run django development server
CMD cd sandbox && \
    python manage.py runserver 0.0.0.0:8000

# ---- Production image ----
FROM core AS production

ENV PYTHONUNBUFFERED=1

WORKDIR /app/sandbox

# The default command runs gunicorn WSGI server in the sandbox
CMD gunicorn -c /usr/local/etc/gunicorn/ashley.py wsgi:application
