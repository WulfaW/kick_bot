FROM python:3.12-slim-bullseye

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Debian Bullseye has all the required font packages, unlike Bookworm.
# This prevents the apt-get errors and is much faster to build than the 2GB official image!
RUN playwright install --with-deps chromium

COPY . .

CMD ["python", "main.py"]
