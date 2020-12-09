FROM python:3.7-slim

RUN apt-get update && apt-get install -y curl build-essential

## Poetry setup
ENV POETRY_VERSION=1.1.3 \
  # make poetry install to this location
  POETRY_HOME="/opt/poetry" \
  # make poetry not use virtual envs
  POETRY_VIRTUALENVS_CREATE=false \
  # do not ask any interactive question
  POETRY_NO_INTERACTION=1
# prepend poetry to path
ENV PATH="$POETRY_HOME/bin:$PATH"
# Download and install poetry
RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -

WORKDIR /app
COPY pyproject.toml ./
# Install dependencies
RUN poetry install --no-root
COPY . ./

CMD ["poetry", "run", "python", "main.py"]
