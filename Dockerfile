FROM mambaorg/micromamba:latest

# Set working directory
USER root
WORKDIR /app

# System dependencies
RUN apt-get update && apt-get install -y \
    curl bzip2 git build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install base Python for the orchestrator layer via micromamba
RUN micromamba install -y -n base -c conda-forge python=3.11 pip && \
    micromamba clean --all --yes

# This activates the conda env for all subsequent RUN steps
ARG MAMBA_DOCKERFILE_ACTIVATE=1

# Copy source code
COPY . .

# Install orchestrator dependencies
RUN pip install -r requirements.txt

# Install local package
RUN pip install -e .

# ENV vars for metaflow
ENV USER=mlops
ENV METAFLOW_USER=mlops
ENV METAFLOW_HOME=/app/.metaflow
ENV PATH="/opt/conda/bin:$PATH"

# Default command
CMD ["python", "-m", "flows.training_flow", "--environment=pypi", "run"]