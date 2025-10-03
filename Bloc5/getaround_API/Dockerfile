FROM python:3.10-slim

# Create non-root user for Hugging Face
RUN useradd -m -u 1000 user
USER user

ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

WORKDIR $HOME/app

# Copy project files with correct ownership
COPY --chown=user . $HOME/app

# Install dependencies
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Launch FastAPI with uvicorn
CMD ["uvicorn", "mlapi:app", "--host", "0.0.0.0", "--port", "7860"]
