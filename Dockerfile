FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY pyproject.toml .
COPY src/ src/
COPY tests/ tests/
COPY scripts/ scripts/

# Install package and test runner
RUN pip install -e . && pip install pytest

# Default: run tests
CMD ["sh", "-c", "pytest -q tests/ && python -m compileall src/ && echo '✅ All tests passed'"]
