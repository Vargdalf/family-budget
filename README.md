# family-budget

## How to run:

- Clone repo
- make prepare (migrations, creating superuser, loading fixtures)
- make run (docker-compose up)

## How to run withour docker-compose:

- Clone repo
- Install [Pipenv](https://pipenv.pypa.io/en/latest/install/#installing-pipenv)
- pipenv install --dev
- python manage.py migrate
- python manage.py runserver

## Endpoint:

- /admin/
- /api/
- /api/openapi/ (schema)