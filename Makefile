DOCKER_COMPOSE_DEV = docker-compose
DOCKER_COMPOSE_CI = docker-compose -f docker-compose.yml
DOCKER_COMPOSE = $(DOCKER_COMPOSE_DEV)


PEERSCOUT_PYTHON = $(DOCKER_COMPOSE) run --rm --user elife peerscout python


PYTEST_ARGS =
STEP =
SQL =
NO_BUILD =
ARGS =


.PHONY: all test clean build logs


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


client-watch: client-build
	$(DOCKER_COMPOSE) run --rm client npm run ~test


client-shell: client-build
	$(DOCKER_COMPOSE) run --rm client bash


server-build:
	# only dev compose file has "init" service defined
	@if [ "$(DOCKER_COMPOSE)" = "$(DOCKER_COMPOSE_DEV)" ] && [ "$(NO_BUILD)" != "y" ]; then \
		$(DOCKER_COMPOSE) build init; \
	fi
	@if [ "$(NO_BUILD)" != "y" ]; then \
		$(DOCKER_COMPOSE) build client peerscout; \
	fi


server-build-dev:
	$(DOCKER_COMPOSE) build peerscout-base-dev peerscout-dev


server-test: server-build-dev
	$(DOCKER_COMPOSE) run --rm peerscout-dev ./project_tests.sh


server-test-pytest: server-build-dev
	$(DOCKER_COMPOSE) run --rm peerscout-dev pytest $(PYTEST_ARGS)


server-watch: server-build-dev
	$(DOCKER_COMPOSE) run --rm peerscout-dev pytest-watch -- $(PYTEST_ARGS)


server-dev-shell: server-build-dev
	$(DOCKER_COMPOSE) run --rm peerscout-dev bash


db-start:
	$(DOCKER_COMPOSE) up -d db


db-shell:
	$(DOCKER_COMPOSE) exec db bash


db-sql-shell:
	$(DOCKER_COMPOSE) exec db psql \
		--username=peerscout_user \
		peerscout_db


.require-SQL:
	@if [ -z "$(SQL)" ]; then \
		echo "SQL required"; \
		exit 1; \
	fi


db-run-sql: .require-SQL
	$(DOCKER_COMPOSE) exec db psql \
		--username=peerscout_user \
		peerscout_db \
		-c "$(SQL)"


migrate-schema: server-build
	$(DOCKER_COMPOSE) run --rm --user elife peerscout ./migrate-schema.sh


update-data-and-reload: server-build
	$(DOCKER_COMPOSE) run --rm --user elife peerscout ./update-data-and-reload.sh


run-preprocessing-step: server-build
	$(PEERSCOUT_PYTHON) -m peerscout.preprocessing.$(STEP) $(ARGS)


fix-data-permissions:
	mkdir -p .data
	chmod -R a+w .data


start: server-build
	$(DOCKER_COMPOSE) up -d peerscout


stop:
	$(DOCKER_COMPOSE) stop peerscout


www-shell:
	$(DOCKER_COMPOSE) exec peerscout bash


www-shell-run:
	$(DOCKER_COMPOSE) run --rm peerscout bash


elife-shell:
	$(DOCKER_COMPOSE) exec --user elife peerscout bash


elife-shell-run:
	$(DOCKER_COMPOSE) run --rm --user elife peerscout bash


restart: stop start


down:
	$(DOCKER_COMPOSE) down


clean:
	$(DOCKER_COMPOSE) down -v


logs:
	$(DOCKER_COMPOSE) logs -f


build: .PHONY
	$(DOCKER_COMPOSE) build client peerscout


ci-build-and-test:
	make DOCKER_COMPOSE="$(DOCKER_COMPOSE_CI)" build server-build client-test server-test


ci-clean:
	$(DOCKER_COMPOSE_CI) down -v
