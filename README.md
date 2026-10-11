# Team Project

Building with Docker:
```
docker build -t inf1103-teamproject .
```
Running with Docker:
```
docker run --rm -it -v "${PWD}:/usr/src/app" inf1103-teamproject
```
Running the test script with Docker:
```
docker run --rm inf1103-teamproject python test_main.py
```

---

To run the project without Docker, install Python requirements first:
```
pip install -r requirements.txt
```
Then, run the program:
```
python main.py
```
Alternatively, run the automated test script:
```
python test_main.py
```