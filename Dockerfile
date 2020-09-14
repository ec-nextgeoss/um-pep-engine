# Base container
FROM python:3.6

WORKDIR /pep

# Add code
COPY src/ .

RUN pip install -r requirements.txt

# Declare and expose service listening port
EXPOSE 5566/tcp

# Declare entrypoint of that exposed service
ENTRYPOINT ["python3", "./main.py"]
