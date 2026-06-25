FROM python:3.11-slim

WORKDIR /app

# Copy source code
COPY pyproject.toml .
COPY src/ src/
COPY tests/ tests/
COPY scripts/ scripts/

# Setup venv and install
RUN python3 -m venv /opt/venv && \
    /opt/venv/bin/pip install --upgrade pip && \
    /opt/venv/bin/pip install pytest && \
    /opt/venv/bin/pip install hatchling

ENV PATH="/opt/venv/bin:$PATH"
ENV PYTHONPATH="/app/src:$PYTHONPATH"

# Default: run tests
CMD ["sh", "-c", "pytest -q tests/ && python -m compileall src/ && echo '✅ All tests passed'"]
