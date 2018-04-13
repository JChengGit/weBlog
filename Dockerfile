
FROM python:3.6.4

COPY ./requirements.txt /requirements.txt
COPY ./server.py /server.py
COPY ./templates/ /templates/
COPY ./static/ /static/

RUN pip install -r requirements.txt
EXPOSE 3000
CMD python server.py

