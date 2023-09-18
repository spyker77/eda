# ---- Build Stage ----
FROM python:3.11-alpine AS build

WORKDIR /code

# Install curl, use it to install poetry, then remove curl
RUN apk --no-cache add curl && \
    curl -sSL https://install.python-poetry.org | python3 - --version 1.6.1 && \
    apk del curl

# Copy only the files needed for installing dependencies
COPY pyproject.toml poetry.lock ./

# Install dependencies
RUN pip install --upgrade pip --no-cache-dir && \
    export PATH="/root/.local/bin:$PATH" && \
    poetry config virtualenvs.create false && \
    poetry install --without dev

# ---- Final Stage ----
FROM python:3.11-alpine

WORKDIR /code

# Install bash
RUN apk --no-cache add bash && \
    rm -rf /var/cache/apk/*

# Copy wait-for-it script and make it executable
COPY wait-for-it.sh /wait-for-it.sh
RUN chmod +x /wait-for-it.sh && adduser -D app

# Copy built python dependencies from build stage
COPY --from=build /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=build /usr/local/bin /usr/local/bin

# Copy the rest of the application
COPY . .

# Switch to non-root user
USER app

CMD [ "python", "-m", "app.main" ]
