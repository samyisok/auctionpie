stop:
	docker-compose stop

start: run

run:
	docker-compose up --remove-orphans -d

build:
	docker-compose up --build

restart: stop start