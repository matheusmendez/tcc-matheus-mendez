FROM python:3.12.3-bullseye

WORKDIR /app

COPY requirements.txt .

RUN pip3 install -r requirements.txt

COPY ./web_server .

EXPOSE 5000

CMD ["python3", "app.py"]