FROM python:3.11-slim
ARG VCFIGHTER_BUILD=V10-FINAL-ALLVC-FIX-20260918
RUN echo "Building $VCFIGHTER_BUILD"

RUN apt-get update \
    && apt-get install -y --no-install-recommends ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
# Hard fail if an obsolete ALLVC implementation is present in the build context.
RUN ! grep -R "self\.calls\.app\.get_dialogs" -n relay main.py commands.py 2>/dev/null

CMD ["python", "main.py"]
