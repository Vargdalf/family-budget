# syntax=docker/dockerfile:1
FROM python:3.9
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=family_budget.settings
WORKDIR /code
COPY . /code/
RUN pip install pipenv
RUN pipenv install --deploy --ignore-pipfile
RUN pipenv run /code/manage.py collectstatic --noinput