stop:
	docker-compose stop

start: run

run:
	docker-compose up --remove-orphans -d

restart: stop start