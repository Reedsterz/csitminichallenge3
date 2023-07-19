FROM python:3
WORKDIR /python-docker
COPY server.py server.py
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
EXPOSE 8080
CMD ["python3", "server.py"]
