stop:
	docker-compose stop

start: run

run:
	docker-compose up --remove-orphans -d

build:
	touch env.django.secret
	docker-compose up --build

test:
	isort .
	docker exec django bash -c 'coverage erase && coverage run -m pytest -s'

coverage:
	docker exec django bash -c 'coverage report && coverage html'

restart: stop start

readme:
	cat ./doc/README-header.rst > ./README.rst
	python ./doc/get_graphql_doc.py >> ./README.rst
	echo "Test coverage" >> ./README.rst
	echo "=============" >> ./README.rst
	echo '::' >> ./README.rst
	echo '' >> ./README.rst
	docker exec django bash -c 'coverage report'| sed -e 's/^/  /g' >> ./README.rst


migration:
	docker exec django bash -c 'python manage.py makemigrations && python manage.py migrate'
