FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Create a non-root user to run the app
RUN useradd -m appuser
USER appuser

# Run using gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "run:app"]

EXPOSE 5000