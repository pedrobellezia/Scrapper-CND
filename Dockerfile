FROM mcr.microsoft.com/playwright/python:v1.58.0-jammy

RUN apt-get update && apt-get install -y \
    xvfb \
    x11-utils \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

RUN xvfb-run -a --server-args="-screen 0 1920x1080x24" playwright install chromium

EXPOSE 5049

CMD ["python", "-m", "app.app"]
