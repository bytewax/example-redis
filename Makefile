.DEFAULT_GOAL := compose-up

@build-writer:
	docker build \
		-f docker/redis-publisher.Dockerfile \
		-t redis-publisher \
		.

@run-writer:
	docker run redis-publisher

compose-up:
	docker compose up
