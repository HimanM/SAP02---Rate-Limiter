FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files into the rateguard package directory
COPY app.py middleware.py proxy.py config.py token_bucket.lua /app/rateguard/

# Run the application with Gunicorn
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "rateguard.app:app"]
