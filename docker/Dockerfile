FROM python:3.14 AS build
WORKDIR /app
RUN python -m venv /venv && /venv/bin/python -m pip install --no-cache-dir -U pip
COPY requirements.txt /app
RUN /venv/bin/pip install --no-cache-dir -r requirements.txt
COPY nikolausers /app/nikolausers
COPY sites /app/sites
COPY templates /app/templates
COPY manage.py docker/docker-entrypoint.sh /app/
RUN chmod +x /app/docker-entrypoint.sh

FROM python:3.14-slim
WORKDIR /app
RUN apt-get update && apt-get install --no-install-recommends -y libpq5 && rm -rf /var/lib/apt/lists/*
COPY --from=build /venv /venv
COPY --from=build /app /app
ENTRYPOINT ["/app/docker-entrypoint.sh"]
