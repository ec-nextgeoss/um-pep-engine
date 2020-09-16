# Base container
FROM python:3.6

WORKDIR /pep

COPY src/requirements.txt .

RUN pip install -r requirements.txt

# Add code
COPY src/ .

# Declare and expose service listening port
EXPOSE 5566/tcp

# Declare entrypoint of that exposed service
ENTRYPOINT ["python3", "-u", "./main.py"]
