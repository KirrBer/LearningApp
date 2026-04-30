#!/bin/bash
set -e

# Wait for dependencies if needed
# For example, wait for databases or other services

# Start the application
exec uvicorn main:app --host 0.0.0.0 --port 8000