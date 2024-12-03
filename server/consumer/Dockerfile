FROM python:3.10-slim

WORKDIR /consumer

COPY . /consumer
RUN pip install --no-cache-dir -r requirements.txt

CMD [ "python", "./consumer.py" ]
