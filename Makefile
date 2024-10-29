run-migration:
	alembic upgrade head && alembic revision --autogenerate -m 'Initial migration'

run-docker:
	docker-compose up

stop-docker:
	docker-compose down
	docker rmi blog