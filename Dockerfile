FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    wget gnupg unzip curl supervisor \
    && rm -rf /var/lib/apt/lists/*

RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | gpg --dearmor > /usr/share/keyrings/google-linux-signing-keyring.gpg \
    && echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-linux-signing-keyring.gpg] http://dl.google.com/linux/chrome/deb/ stable main" \
       > /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

RUN CHROME_VERSION=$(google-chrome --version | awk '{print $3}' | cut -d. -f1) \
    && DRIVER_VERSION=$(curl -s "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_${CHROME_VERSION}") \
    && wget -q "https://chromedriver.storage.googleapis.com/${DRIVER_VERSION}/chromedriver_linux64.zip" -O /tmp/chromedriver.zip \
    && unzip /tmp/chromedriver.zip -d /usr/local/bin \
    && rm /tmp/chromedriver.zip \
    && chmod +x /usr/local/bin/chromedriver

WORKDIR /app

COPY pyproject.toml README.md ./
COPY . .

RUN pip install --upgrade pip && pip install .

ENV CHROMEDRIVER_PATH=/usr/local/bin/chromedriver
ENV DATABASE_PATH=/app/scraped_data.db
ENV LOG_LEVEL=INFO
ENV API_HOST=0.0.0.0
ENV API_PORT=8000
ENV DASHBOARD_PORT=8501

COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

EXPOSE 8000
EXPOSE 8501

CMD ["supervisord", "-n"]

