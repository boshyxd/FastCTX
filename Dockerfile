FROM python:3.11-slim-buster

WORKDIR /app

COPY pyproject.toml ./ 

# Install uv
RUN pip install uv

# Create a virtual environment and install dependencies
RUN uv venv
RUN . .venv/bin/activate && uv pip sync pyproject.toml

COPY . .

EXPOSE 8000

CMD [".venv/bin/python", "-m", "uvicorn", "ctx.main:app", "--host", "0.0.0.0", "--port", "8000"]
