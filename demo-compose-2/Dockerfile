#Base image  (linux alpine with preinstalled python and pip)
FROM python:3.10-alpine

WORKDIR /

#copy dependencies and install them
COPY ./app/requirements.txt /requirements.txt
RUN  pip3 install -r requirements.txt

#copy source code
COPY ./app/main.py /main.py
COPY ./app/db.py /db.py

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8866", "--workers", "2"]
