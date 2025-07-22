# Use Python 3.11 slim image (FastMCP requires 3.10+)
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install the published package from PyPI
RUN pip install --no-cache-dir sensortower-mcp

# Create non-root user
RUN useradd --create-home --shell /bin/bash app
USER app

# Expose default port
EXPOSE 8666

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8666/health || exit 1

# Default command (stdio mode for MCP clients)
CMD ["sensortower-mcp", "--transport", "stdio"] 