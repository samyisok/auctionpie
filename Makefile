stop:
	docker-compose stop

start: run

run:
	docker-compose up --remove-orphans -d

build:
	docker-compose up --build

test:
	isort .
	docker exec django bash -c 'coverage erase && coverage run -m pytest -s'

coverage:
	docker exec django bash -c 'coverage report && coverage html'

restart: stop start