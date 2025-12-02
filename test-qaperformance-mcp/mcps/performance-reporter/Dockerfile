FROM python:3.11-slim

# Install mcpo
RUN pip install mcpo

WORKDIR /app

# Copy MCP server files
COPY . .

# Install Python dependencies
RUN pip install -r requirements.txt

# Make server executable
RUN chmod +x server.py

# Expose port
EXPOSE 8001

# Start MCP server with mcpo HTTP wrapper
CMD mcpo --host 0.0.0.0 --port 8001 -- python server.py