FROM python:3
MAINTAINER Izak Fritz "izakfr@umich.edu"
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
ENTRYPOINT ["python"]
CMD ["restAPI.py"]
