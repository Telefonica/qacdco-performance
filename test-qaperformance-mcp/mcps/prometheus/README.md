# Prometheus MCP Server

MCP server that enables AI agents to query and analyze Prometheus metrics through standardized interfaces.

## Overview

This MCP server connects to your Prometheus instance to:
- Execute instant PromQL queries
- Execute range queries with time/step parameters
- List all available metrics
- Get metric metadata
- Check scrape target information
- Perform health checks

## Configuration

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `PROMETHEUS_URL` | Prometheus server endpoint URL | Yes | - |
| `PROMETHEUS_URL_SSL_VERIFY` | Enable/disable SSL certificate verification | No | `true` |
| `PROMETHEUS_DISABLE_LINKS` | Disable UI links to conserve tokens | No | `false` |

### Optional Authentication

For authenticated Prometheus instances, you can add:

| Variable | Description |
|----------|-------------|
| `PROMETHEUS_USERNAME` | Basic auth username |
| `PROMETHEUS_PASSWORD` | Basic auth password |
| `PROMETHEUS_TOKEN` | Bearer token for authentication |

## Available Tools

The MCP server exposes the following tools:

1. **health_check** - Health check endpoint for container monitoring
2. **execute_query** - Run instant PromQL queries
3. **execute_range_query** - Execute range queries with time/step parameters
4. **list_metrics** - List all available metrics in Prometheus with pagination
5. **get_metric_metadata** - Retrieve metric-specific metadata
6. **get_targets** - Display scrape target information

## Usage Examples

### Query CPU Usage
```promql
rate(cpu_usage_seconds_total[5m])
```

### Query Memory Usage
```promql
container_memory_usage_bytes{container="my-app"}
```

### Range Query for Response Time
```promql
http_request_duration_seconds{job="api"}
```

## Implementation

Uses the Python-based MCP server from: https://github.com/pab1it0/prometheus-mcp-server

Clones and installs the repository directly in the Docker container.

## Port

Exposed on port **8002** in the docker-compose setup.

## References

- [Prometheus MCP Server GitHub](https://github.com/pab1it0/prometheus-mcp-server)
- [Docker MCP Catalog](https://hub.docker.com/mcp/server/prometheus/overview)
