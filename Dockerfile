FROM python:3.9-slim

WORKDIR /app

# Install poetry
RUN pip install poetry

# Copy project files
COPY pyproject.toml poetry.lock* ./
COPY README.md ./
COPY leela/ ./leela/
COPY prompts/ ./prompts/
COPY run_server.py ./

# Configure poetry to not use a virtual environment in the container
RUN poetry config virtualenvs.create false \
    && poetry install --no-dev --no-interaction --no-ansi

# Create necessary directories
RUN mkdir -p data/ideas

# Expose port
EXPOSE 8000

# Run the server
CMD ["python", "run_server.py"]