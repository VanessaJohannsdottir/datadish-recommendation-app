#!/bin/bash

echo "⏳ Waiting for Streamlit to become healthy..."

# Start container in background
docker-compose up -d

# Wait until healthcheck reports 'healthy'
until [ "$(docker inspect -f '{{.State.Health.Status}}' datadish-dashboard)" == "healthy" ]; do
  echo "Still starting... waiting..."
  sleep 30
done

echo "✅ Streamlit is ready at http://localhost:8501"
# Open browser depending on platform
if which xdg-open > /dev/null; then
  xdg-open http://localhost:8501
elif which open > /dev/null; then
  open http://localhost:8501
else
  echo "🌐 Please open http://localhost:8501 manually in your browser."
fi