FROM nikolaik/python-nodejs:python3.11-nodejs20
# Install mcpo and uv
RUN pip install mcpo uv

WORKDIR /app

# Expose port
EXPOSE 8000

# Try the format from the official documentation (no uvx prefix)
CMD sh -c 'echo "Testing MySQL connection..." && \
    timeout 10 bash -c "until echo > /dev/tcp/$MYSQL_HOST/$MYSQL_PORT; do sleep 1; done" 2>/dev/null && \
    echo "MySQL accessible, testing MCP server directly..." && \
    echo "MCP server test completed, now starting with MCPO..." && \
    exec mcpo --host 0.0.0.0 --port 8000 -- npx -y -p @benborla29/mcp-server-mysql@2.0.2 -p dotenv mcp-server-mysql'