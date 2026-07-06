# ----------------------------------------------------------------------------------
# Stage 1: Builder
# ----------------------------------------------------------------------------------
FROM ghcr.io/astral-sh/uv:python3.14-bookworm-slim AS builder

WORKDIR /app

# Disable UV's automatic Python downloads since we're using the
# base image's Python in the runtime stage
ENV UV_PYTHON_DOWNLOADS=0

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# Copy from the cache instead of linking since it's a mounted volume
ENV UV_LINK_MODE=copy

# Omit development dependencies
ENV UV_NO_DEV=1

# Ensure installed tools can be executed out of the box
ENV UV_TOOL_BIN_DIR=/usr/local/bin

# Install the project's dependencies using the lockfile and settings
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev

# Add the rest of the project source code and install it in the builder stage
COPY . /app

# Sync again to install the local project into the .venv
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

# ----------------------------------------------------------------------------------
# Stage 2: Final (Runtime)
# ----------------------------------------------------------------------------------
FROM python:3.14-slim-bookworm AS final

ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8

# Setup a non-root user (repeat from builder)
RUN groupadd --system --gid 999 nonroot \
    && useradd --system --gid 999 --uid 999 --create-home nonroot

WORKDIR /app
RUN chown nonroot:nonroot /app

# Copy the virtual environment and the app code with correct ownership
COPY --from=builder --chown=nonroot:nonroot /app/.venv /app/.venv
COPY --from=builder --chown=nonroot:nonroot /app /app

# Set environment variables so Python and the shell find the packages
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

# Switch to non-root user
USER nonroot

# Run the application using uvicorn
CMD ["sh", "-c", "python manage.py migrate && python manage.py checksuperuserexists && daphne -b 0.0.0.0 -p 8000 main.asgi:application"]
