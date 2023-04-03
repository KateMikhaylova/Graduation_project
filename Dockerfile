FROM python:3.9

ENV PYTHONDONTWRITEBYTECODE 1

ENV PYTHONUNBUFFERED 1


WORKDIR /code
COPY . /code
RUN pip install -r /code/requirements.txt
RUN chmod +x ./entrypoint.sh

ENTRYPOINT ["/code/entrypoint.sh"]
