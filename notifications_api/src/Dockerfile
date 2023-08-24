FROM python:3.10

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY requirements.txt requirements.txt


RUN pip install --upgrade pip \
    && pip install -r /app/requirements.txt

COPY . ./src

CMD ["/bin/sh", "-c", "gunicorn -k uvicorn.workers.UvicornWorker --chdir src main:app --bind 0.0.0.0:8000"]