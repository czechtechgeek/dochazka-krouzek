FROM python:3-alpine

WORKDIR /app

ENV SQLITE_URL="sqlite:////config/dochazka.db"
ENV PORT=9120
ENV PYTHONUNBUFFERED=1
ENV INGRESS_BASE=/api/hassio_ingress/dochazka

RUN mkdir -p /config

COPY src/requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

COPY src/app.py src/models.py ./
COPY src/templates/ templates/
COPY src/static/ static/

EXPOSE 9120

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s \
  CMD python3 -c "import urllib.request; urllib.request.urlopen('http://localhost:9120/')" || exit 1

CMD ["python3", "-u", "app.py"]