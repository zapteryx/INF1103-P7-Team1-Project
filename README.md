# Team Project

## Quick Start (Running pre-built Docker image):
Our CI/CD pipeline builds a Docker image and pushes it to GitHub Container Registry (GHCR).

To pull the latest image and run it, use the following command:
```bash
docker pull ghcr.io/zapteryx/inf1103-p7-team1-project:latest
```
Running the pulled image with Docker:
```bash
docker run --rm -it -v "${PWD}:/usr/src/app" ghcr.io/zapteryx/inf1103-p7-team1-project:latest
```
Running the test script with Docker:
```bash
docker run --rm ghcr.io/zapteryx/inf1103-p7-team1-project:latest python test_main.py
```

---

## Building with Docker:
Running the build command:
```bash
docker build -t inf1103-teamproject .
```
Running the built image with Docker:
```bash
docker run --rm -it -v "${PWD}:/usr/src/app" inf1103-teamproject
```
Running the test script with Docker:
```bash
docker run --rm inf1103-teamproject python test_main.py
```

---

## Running without Docker:
To run the project without Docker, install Python requirements first:
```bash
pip install -r requirements.txt
```
Then, run the program:
```bash
python main.py
```
Alternatively, run the automated test script:
```bash
python test_main.py
```