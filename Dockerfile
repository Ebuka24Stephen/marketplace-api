FROM python:3.12-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install build tools & dev libraries for compiled packages
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    libjpeg-dev \
    zlib1g-dev \
 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/

RUN pip install --user --no-cache-dir -r requirements.txt


FROM python:3.12-slim AS final 


WORKDIR /app

COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

COPY . .

CMD ["gunicorn", "marketplace.wsgi:application", "--bind", "0.0.0.0:8000"]