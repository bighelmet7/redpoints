FROM python:latest

RUN apt-get update && apt-get upgrade -y

ADD . /application
WORKDIR /application
RUN pip install -r requirements.txt

VOLUME /vol/dependencies

EXPOSE 5000
CMD ["gunicorn", "-b", "0.0.0.0:5000", "-t", "1200", "application:app"]
