FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY server.py ./server.py

# MCP servers use stdio; this keeps the container running for a client to connect.
CMD ["python", "server.py"]
