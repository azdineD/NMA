FROM python:3.10

WORKDIR /app

COPY . /app

RUN pip install --upgrade pip
RUN pip install flask flask_sqlalchemy psycopg2-binary

EXPOSE 5000

CMD ["python", "app.py"]
