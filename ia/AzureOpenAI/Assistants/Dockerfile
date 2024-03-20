FROM python:3-alpine

WORKDIR /app
COPY requirements.txt /app/requirements.txt

RUN pip install --upgrade pip && \
    pip install -r requirements.txt

COPY . /app

# Comando para ejecutar tu aplicación
CMD ["python", "PerformanceAnalizer.py"]
