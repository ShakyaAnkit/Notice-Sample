# Text Doc that contains all the commands that user could call on command line to call an image
FROM python:3.8-slim-buster
# To see output of application in real time
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONBUFFERED=1 

# Our working directory
WORKDIR /app

COPY requirements.txt /app
# RUN pip uninstall django example 
RUN pip install -r requirements.txt

COPY . /app/    


