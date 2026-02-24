FROM python:3.12-slim

# System deps for Camoufox / Playwright browsers + Mesa for WebGL software rendering
RUN apt-get update && apt-get install -y --no-install-recommends \
    xvfb \
    fonts-liberation \
    fonts-noto-color-emoji \
    libgtk-3-0 \
    libdbus-glib-1-2 \
    libxt6 \
    libx11-xcb1 \
    libasound2 \
    libgl1-mesa-dri \
    libglx-mesa0 \
    libegl-mesa0 \
    libgbm1 \
    && rm -rf /var/lib/apt/lists/*

ENV LIBGL_ALWAYS_SOFTWARE=1

WORKDIR /app
COPY pyproject.toml .

RUN pip install --no-cache-dir . \
    && python -m camoufox fetch

COPY app.py .

EXPOSE 8191

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8191"]
