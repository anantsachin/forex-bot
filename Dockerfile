# Read the doc: https://huggingface.co/docs/hub/spaces-sdks-docker
FROM python:3.9

# Set up a new user named "user" with user ID 1000
RUN useradd -m -u 1000 user
USER user
# Switch to the "user" user
ENV PATH="/home/user/.local/bin:$PATH"

WORKDIR /app

# Copy requirements file to the working directory
COPY --chown=user backend/requirements.txt requirements.txt

# Install dependencies
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Copy the current directory contents into the container at /app
COPY --chown=user backend/ .

# Expose port 7860
EXPOSE 7860

# CMD to start the uvicorn server on port 7860
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
