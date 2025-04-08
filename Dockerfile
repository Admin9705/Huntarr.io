FROM python:3.9-slim
WORKDIR /app
# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
# Install Flask for the web interface
RUN pip install --no-cache-dir flask
# Copy application files
COPY *.py ./
COPY utils/ ./utils/
COPY web_server.py ./
# Create templates directory and copy index.html
RUN mkdir -p templates static/css static/js
COPY templates/ ./templates/
COPY static/ ./static/
# Create required directories
RUN mkdir -p /config/stateful /config/settings
# Default environment variables
ENV API_KEY="your-api-key" \
API_URL="http://your-sonarr-address:8989" \
API_TIMEOUT="60" \
HUNT_MISSING_SHOWS=1 \
HUNT_UPGRADE_EPISODES=5 \
SLEEP_DURATION=900 \
STATE_RESET_INTERVAL_HOURS=168 \
RANDOM_SELECTION="true" \
MONITORED_ONLY="true" \
DEBUG_MODE="false" \
ENABLE_WEB_UI="true" \
SKIP_FUTURE_EPISODES="true" \
SKIP_SERIES_REFRESH="false"
# Create volume mount points
VOLUME ["/config"]
# Expose web interface port
EXPOSE 8988
# Add startup script that conditionally starts the web UI
COPY start.sh .
RUN chmod +x start.sh
# Run the startup script which will decide what to launch
CMD ["./start.sh"]