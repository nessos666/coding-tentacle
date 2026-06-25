FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY pyproject.toml .
COPY src/ src/
COPY tests/ tests/
COPY scripts/ scripts/

# Setup venv and install
RUN python3 -m venv /opt/venv && \
    /opt/venv/bin/pip install --upgrade pip && \
    /opt/venv/bin/pip install -e . && \
    /opt/venv/bin/pip install pytest

ENV PATH="/opt/venv/bin:$PATH"

# Default: run tests
CMD ["sh", "-c", "pytest -q tests/ && python -m compileall src/ && echo '✅ All tests passed'"]
