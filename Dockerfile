# Use the official Python 3.8 image as the base image
FROM python:3.8

# Set the working directory inside the container
WORKDIR /app

# Copy the source code into the container
COPY src /app/src

# Copy the requirements.txt file into the container
COPY requirements.txt /app

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Set the entrypoint to start the main.py script
CMD ["python", "src/main.py", "us", "--file", "/app/data/unchained.sock"]
