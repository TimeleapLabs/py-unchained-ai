# Use the official Python 3.8 image as the base image
FROM pytorch/pytorch:2.3.1-cuda11.8-cudnn8-devel

# Set the working directory inside the container
WORKDIR /app

# Copy the source code into the container
COPY src /app/src

# Update Python to 3.8.19
RUN conda update -n base -c defaults conda && \
    conda install -y python=3.8.19 && \
    conda update --all --yes

# Copy the requirements.txt file into the container
COPY requirements.txt /app

# Install the Python dependencies
RUN /opt/conda/bin/pip install --no-cache-dir -r requirements.txt

# Set the entrypoint to start the main.py script
CMD ["python", "src/main.py", "us", "--file", "/app/data/unchained.sock"]
