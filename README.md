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
Running the test scripts with Docker:
```bash
docker run --rm ghcr.io/zapteryx/inf1103-p7-team1-project:latest python scripts/test_main.py
docker run --rm ghcr.io/zapteryx/inf1103-p7-team1-project:latest python scripts/test_authentication.py
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
Running the test scripts with Docker:
```bash
docker run --rm inf1103-teamproject python scripts/test_main.py
docker run --rm inf1103-teamproject python scripts/test_authentication.py
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
Alternatively, run the automated test scripts:
```bash
python scripts/test_main.py
python scripts/test_authentication.py
```

## Authentication System
The application includes a secure multi-user authentication system:
- **User Registration**: Secure password requirements (12+ chars, uppercase, lowercase, digit, symbol)
- **User Login**: Argon2 password hashing for secure credential storage
- **Session Management**: User sessions tracked throughout application usage
- **Account Management**: Support for active/inactive account status

All user authentication data is stored in SQLite (`clients.db`) with the UserManager backend.