migrate:
	docker-compose run web pipenv run python manage.py migrate

createuser:
	docker-compose run web pipenv run python manage.py createsuperuser --email mail@mail.com

up:
	docker-compose up

loadfixtures:
	docker-compose run web pipenv run python manage.py loaddata users/fixtures/*.json budgets/fixtures/*.json

prepare: migrate createuser loadfixtures

run: up