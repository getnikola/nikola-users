FROM python:3.14-alpine AS build
WORKDIR /app
RUN apk add build-base libpq libpq-dev
RUN python -m venv /venv && /venv/bin/python -m pip install --no-cache-dir -U pip
COPY requirements.txt /app
RUN /venv/bin/pip install --no-cache-dir -r requirements.txt
COPY nikolausers /app/nikolausers
COPY sites /app/sites
COPY templates /app/templates
COPY manage.py docker/docker-entrypoint.sh /app/
RUN chmod +x /app/docker-entrypoint.sh

FROM python:3.14-alpine
WORKDIR /app
RUN apk add libpq
COPY --from=build /venv /venv
COPY --from=build /app /app
ENTRYPOINT ["/app/docker-entrypoint.sh"]
