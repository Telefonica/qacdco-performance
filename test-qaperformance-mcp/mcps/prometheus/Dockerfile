FROM python:3.11-slim

# Install git and other dependencies
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# Install mcpo and uv
RUN pip install --no-cache-dir mcpo uv

WORKDIR /app

# Clone the prometheus-mcp-server repository
RUN git clone https://github.com/pab1it0/prometheus-mcp-server.git /app/prometheus-mcp-server

WORKDIR /app/prometheus-mcp-server

# Install the package with uv
RUN uv pip install --system -e .

# Expose port
EXPOSE 8002

WORKDIR /app

# Start MCP server with mcpo HTTP wrapper
# Using the installed script entry point
CMD mcpo --host 0.0.0.0 --port 8002 -- prometheus-mcp-server
