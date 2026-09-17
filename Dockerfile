FROM python:3.11-slim
ARG VCFIGHTER_BUILD=V8-ALLVC-FIX
RUN echo "Building $VCFIGHTER_BUILD"

RUN apt-get update \
    && apt-get install -y --no-install-recommends ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

CMD ["python", "main.py"]
