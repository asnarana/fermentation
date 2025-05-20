FROM python:3.10-slim

# 1) Install OS packages needed by many Python extensions
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      build-essential \
      libpq-dev \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 2) Copy and upgrade pip/tools first (leverages Docker cache)
COPY requirements.txt .
RUN pip install --upgrade pip setuptools wheel

# 3) Install your Python deps (no-cache-dir but verbose)
RUN pip install --no-cache-dir -r requirements.txt --verbose

# 4) Copy the rest of your app
COPY . .

EXPOSE 8050
CMD ["python", "app.py"]