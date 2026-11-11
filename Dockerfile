FROM python:3.12.12-slim-bookworm
RUN apt-get update && apt-get install -y --no-install-recommends g++ && rm -rf /var/lib/apt/lists/*
WORKDIR /work
COPY requirements-assay.txt .
RUN python -m pip install --no-cache-dir -r requirements-assay.txt
COPY . .
ENV OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
CMD ["python", "reproduce_release.py"]
