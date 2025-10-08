FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

# Install system dependencies for Pillow + build tools
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    build-essential \
    libjpeg-dev \
    zlib1g-dev \
    libfreetype6-dev \
    liblcms2-dev \
    libopenjp2-7-dev \
    libtiff-dev \
    tk-dev \
    tcl-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "app.py"]
