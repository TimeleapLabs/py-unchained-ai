# Use the NVIDIA CUDA image as the base image
FROM nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu22.04

# Set shell options for better error handling
SHELL ["/bin/bash", "-xe", "-o", "pipefail", "-c"]

# Environment variables for Python, Conda and Miniforge
ENV PYTHON_VERSION=3.8.19
ENV CONDA_DIR=/opt/conda
ENV PATH=$CONDA_DIR/bin:$PATH
ENV MINIFORGE3_VERSION=24.3.0-0

# Set the working directory inside the container
WORKDIR /app

# Copy the source code into the container
COPY src /app/src

# ARG to suppress interaction during package installation
ARG DEBIAN_FRONTEND=noninteractive

# Install curl and Miniforge, clean up unnecessary files afterward
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    --mount=type=cache,target=/var/cache/curl,sharing=locked \
    apt-get update -qy && \
    apt-get install --no-install-recommends -qy curl && \
    pushd /var/cache/curl && \
    curl -sSL -C - -O "https://github.com/conda-forge/miniforge/releases/download/${MINIFORGE3_VERSION}/Miniforge3-${MINIFORGE3_VERSION}-$(uname)-$(uname -m).sh" && \
    /bin/bash Miniforge3-${MINIFORGE3_VERSION}-$(uname)-$(uname -m).sh -b -p "${CONDA_DIR}" && \
    conda clean --tarballs --index-cache --packages --yes && \
    find ${CONDA_DIR} -follow -type f -name '*.a' -delete && \
    find ${CONDA_DIR} -follow -type f -name '*.pyc' -delete && \
    apt-get remove -y --purge curl && \
    apt-get autoremove -y --purge

# Create a Conda environment with PYTHON_VERSION
RUN mamba create -n unchained python=${PYTHON_VERSION} -y && \
    mamba clean -afy

# Activate the environment and install dependencies from requirements.txt
COPY requirements.txt /app
RUN /bin/bash -c "source activate unchained && pip install --no-cache-dir -r requirements.txt && mamba clean -afy && rm requirements.txt"

# Set the entrypoint to start the main.py script, activating the environment first
CMD ["/bin/bash", "-c", "source activate unchained && python src/main.py us --file /app/data/unchained.sock"]
