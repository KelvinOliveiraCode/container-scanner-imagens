# container-scanner-imagens

## Description

Simple Docker image scanner with vulnerability report (MVP). Lists local Docker images using the Docker SDK, falling back to the `docker images` CLI command when the SDK is unavailable. For each image it checks deterministic items such as `latest` tag, missing tag, missing digest, and invalid size, and emits a simple report with findings classified by severity.

Intended for DevOps/Cloud environments. Tests use mocks, so no real Docker is required to run them.

## Stack

- Python 3.9+
- docker SDK (optional; when absent, the program uses the `docker images` CLI)
- pytest (tests)

## Installation

```bash
pip install -e .
```

## Usage

Run the scanner over local images:

```bash
PYTHONPATH=src python -m container_scanner_imagens
```

The `container-scanner` entry point is also available after installation.

Example output with no local images:

```
No local Docker images found.
```

Example output with images:

```
Image: nginx (sha256:aaa123)
  Tags: nginx:latest
  [medium] 'latest' tag detected: the image uses the 'latest' tag, which is mutable and does not guarantee reproducibility.
----------------------------------------
```

## Vulnerability report

For each image, the report emits simple deterministic findings:

- image without tag -> low
- `latest` tag -> medium
- no image digest -> low
- invalid size -> low

Scoring per image: high = 10, medium = 5, low = 1. An image with no findings scores 0.

## Tests

Run the suite with pytest. All tests use mocks (dependency injection via the `client` parameter); none require real Docker.

```bash
PYTHONPATH=src python -m pytest -q
```

Result: 13 tests passed.

## License

MIT

## Author

Kelvin Oliveira
