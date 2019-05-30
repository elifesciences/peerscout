DOCKER_COMPOSE_DEV = docker-compose
DOCKER_COMPOSE_CI = docker-compose -f docker-compose.yml
DOCKER_COMPOSE = $(DOCKER_COMPOSE_DEV)


.PHONY: all test clean build


dev-venv:
	./install.sh


client-build:
	$(DOCKER_COMPOSE) build client


client-bundle: client-build
	$(DOCKER_COMPOSE) run --rm client npm run bundle


client-version: client-build
	$(DOCKER_COMPOSE) run --rm client npm view webpack-cli version


client-test: client-build
	$(DOCKER_COMPOSE) run --rm client ./project_tests.sh


client-shell: client-build
	$(DOCKER_COMPOSE) run --rm client bash


server-build:
	$(DOCKER_COMPOSE) build peerscout


server-build-dev:
	$(DOCKER_COMPOSE) build peerscout-base-dev peerscout-dev


server-test: server-build-dev
	$(DOCKER_COMPOSE) run --rm peerscout-dev ./project_tests.sh


server-shell: server-build
	$(DOCKER_COMPOSE) run --rm peerscout bash


server-dev-shell: server-build-dev
	$(DOCKER_COMPOSE) run --rm peerscout-dev bash


build: .PHONY
	$(DOCKER_COMPOSE) build client peerscout


ci-build-and-test:
	make DOCKER_COMPOSE="$(DOCKER_COMPOSE_CI)" build server-build client-test server-test


ci-clean:
	$(DOCKER_COMPOSE_CI) down -v
