# Dockerfile for Cobalt Core AI Interviewer

# Use official slim Python image
FROM python:3.13-slim

# set working directory
WORKDIR /app

# install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# copy application code
COPY . .

# create a directory for database file if using sqlite
VOLUME ["/app"]

# expose port for uvicorn
EXPOSE 8000

# recommend using environment variables for production settings
# CMD can be overridden by the deploy platform
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
