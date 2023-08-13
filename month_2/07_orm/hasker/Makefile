build:
	docker-compose build

up:
	docker-compose up

down:
	docker-compose down

develop:
	pip install -r requirements.txt
	echo "Starting DB"
	docker run --name hasker_pg_db -p 5432:5432 -e POSTGRES_USER=hasker -e POSTGRES_PASSWORD=hasker_test_site_1 -e POSTGRES_DB=hasker -d postgres:15.2
	sleep 10
	echo "Starting tests"
	python manage.py test --settings=hasker.settings.local
	echo "Starting develop server"
	python manage.py runserver --settings=hasker.settings.local

prod: build up

