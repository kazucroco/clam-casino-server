FROM python:3.11-slim

WORKDIR /clam_casino_server

COPY clam_casino_server/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY clam_casino_server/ .

# We bind to 0.0.0.0 so it's reachable outside the container
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "clam_casino_server:app"]
