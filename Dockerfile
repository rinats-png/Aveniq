FROM python:3.12-slim
WORKDIR /app
COPY . .
RUN useradd --system --uid 10001 --create-home aveniq && mkdir -p /app/data && chown -R aveniq:aveniq /app/data
USER aveniq
ENV PYTHONUNBUFFERED=1 AVENIQ_HOST=0.0.0.0 AVENIQ_PORT=8768 AVENIQ_DB=/app/data/aveniq.db
EXPOSE 8768
CMD ["python", "-m", "aveniq"]
