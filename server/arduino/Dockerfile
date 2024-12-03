FROM python:3.10-slim

WORKDIR /arduino

COPY . /arduino
RUN pip install --no-cache-dir -r requirements.txt

CMD [ "python", "./arduino.py" ]
