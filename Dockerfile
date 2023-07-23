FROM python:3.10

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install netcat-openbsd instead of netcat
RUN apt-get update \
    && apt-get install -y --no-install-recommends netcat-openbsd

WORKDIR /app
COPY Pipfile Pipfile.lock /app/
RUN pip install pipenv && pipenv install --system

COPY . /app/
