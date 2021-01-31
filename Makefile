stop:
	docker-compose stop

start: run

run:
	docker-compose up --remove-orphans -d

build:
	docker-compose up --build

test:
	docker exec django bash -c 'python manage.py test'

restart: stop start