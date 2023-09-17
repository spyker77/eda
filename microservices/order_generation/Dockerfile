FROM python:3.11-slim-buster

WORKDIR /code

RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    curl -sSL https://install.python-poetry.org | python3 - --version 1.6.1 && \
    apt-get purge -y curl && \
    apt-get autoremove -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

COPY pyproject.toml poetry.lock ./
RUN pip install --upgrade pip --no-cache-dir && \
    export PATH="/root/.local/bin:$PATH" && \
    poetry config virtualenvs.create false && \
    poetry install --without dev

COPY wait-for-it.sh /wait-for-it.sh
RUN chmod +x /wait-for-it.sh && useradd -m app
USER app

COPY . .

CMD [ "hypercorn", "app.main:app", "--bind", "0.0.0.0:8000" ]
