PROJECT_NAME=foto

docker_build:
	docker-compose -f docker-compose.yaml --project-name $(PROJECT_NAME) build && \
	docker tag ${PROJECT_NAME}_foto-manager project/$(PROJECT_NAME)

run:
	rm -rf multiproc-tmp && \
	mkdir multiproc-tmp && \
	gunicorn -c gunicorn_cfg.py --bind 0.0.0.0:8080 -w 1 wsgi:app

start:
	docker-compose -f docker-compose.yaml --project-name $(PROJECT_NAME) up -d

stop:
	docker-compose -f docker-compose.yaml --project-name $(PROJECT_NAME) stop

prometheus_reload_config:
	curl 127.0.0.1:9090/-/reload -X POST

