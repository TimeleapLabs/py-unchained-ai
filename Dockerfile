# Use the official Python 3.8 image as the base image
FROM nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu22.04
SHELL ["/bin/bash", "-xe", "-o", "pipefail", "-c"]

# Set the working directory inside the container
WORKDIR /app

# Copy the source code into the container
COPY src /app/src

ARG DEBIAN_FRONTEND=noninteractive
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    apt-get update -qy && \
    apt-get install --no-install-recommends -qy curl && \
    curl -L https://github.com/conda-forge/miniforge/releases/latest/download/Mambaforge-Linux-$(uname -m).sh -o Mambaforge.sh && \
    bash Mambaforge.sh -b -p /opt/conda && \
    rm Mambaforge.sh && \
    apt-get remove -y --purge curl && \
    apt-get autoremove -y --purge

# Update PATH
ENV PATH=/opt/conda/bin:$PATH

# Install Python 3.8.19 using mamba
RUN mamba create -n unchained python=3.8.19 -y \
    && mamba clean -afy

# Activate the environment and install Python packages from requirements.txt
COPY requirements.txt /app
RUN /bin/bash -c "source activate unchained && pip install --no-cache-dir -r requirements.txt && mamba clean -afy && rm requirements.txt"

# Set the environment to activate by default when the container starts
SHELL ["conda", "run", "-n", "unchained", "/bin/bash", "-c"]

# Set the entrypoint to start the main.py script
CMD ["python", "src/main.py", "us", "--file", "/app/data/unchained.sock"]
