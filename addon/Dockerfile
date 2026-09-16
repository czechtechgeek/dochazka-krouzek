ARG BUILD_FROM
FROM $BUILD_FROM

RUN apk add --no-cache python3 py3-pip

WORKDIR /app

COPY requirements.txt .
RUN pip3 install --break-system-packages --no-cache-dir -r requirements.txt

COPY gen_icons.py .
RUN python3 gen_icons.py

COPY run.sh .
RUN chmod +x run.sh

COPY app.py models.py ./
COPY templates/ templates/
COPY static/ static/

# Expose port
EXPOSE 9120

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s \
  CMD python3 -c "import urllib.request; urllib.request.urlopen('http://localhost:9120/')" || exit 1

# Run
CMD ["/app/run.sh"]