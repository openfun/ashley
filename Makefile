# /!\ /!\ /!\ /!\ /!\ /!\ /!\ DISCLAIMER /!\ /!\ /!\ /!\ /!\ /!\ /!\ /!\
#
# This Makefile is only meant to be used for DEVELOPMENT purpose as we are
# changing the user id that will run in the container.
#
# PLEASE DO NOT USE IT FOR YOUR CI/PRODUCTION/WHATEVER...
#
# /!\ /!\ /!\ /!\ /!\ /!\ /!\ /!\ /!\ /!\ /!\ /!\ /!\ /!\ /!\ /!\ /!\ /!\
#
# Note to developpers:
#
# While editing this file, please respect the following statements:
#
# 1. Every variable should be defined in the ad hoc VARIABLES section with a
#    relevant subsection
# 2. Every new rule should be defined in the ad hoc RULES section with a
#    relevant subsection depending on the targeted service
# 3. Rules should be sorted alphabetically within their section
# 4. When a rule has multiple dependencies, you should:
#    - duplicate the rule name to add the help string (if required)
#    - write one dependency per line to increase readability and diffs
# 5. .PHONY rule statement should be written after the corresponding rule
# ==============================================================================
# VARIABLES

# -- Database

DB_HOST            = postgresql
DB_PORT            = 5432

# -- Docker
# Get the current user ID to use for docker run and docker exec commands
DOCKER_UID           = $(shell id -u)
DOCKER_GID           = $(shell id -g)
DOCKER_USER          = $(DOCKER_UID):$(DOCKER_GID)
COMPOSE              = DOCKER_USER=$(DOCKER_USER) docker compose
COMPOSE_RUN          = $(COMPOSE) run --rm
COMPOSE_RUN_APP      = $(COMPOSE_RUN) ashley
COMPOSE_RUN_CROWDIN  = $(COMPOSE_RUN) crowdin -c crowdin/config.yml
COMPOSE_TEST_RUN     = $(COMPOSE_RUN)
COMPOSE_TEST_RUN_APP = $(COMPOSE_TEST_RUN) ashley
MANAGE               = $(COMPOSE_RUN_APP) python sandbox/manage.py
WAIT_DB              = @$(COMPOSE_RUN) dockerize -wait tcp://$(DB_HOST):$(DB_PORT) -timeout 60s
WAIT_ES              = @$(COMPOSE_RUN) dockerize -wait tcp://elasticsearch:9200 -timeout 60s

# -- Node
# We must run node with a /home because yarn tries to write to ~/.yarnrc. If the
# ID of our host user (with which we run the container) does not exist in the
# container (e.g. 1000 exists but 1009 does not exist by default), then yarn
# will try to write to "/.yarnrc" at the root of the system and will fail with a
# permission error.
COMPOSE_RUN_NODE     = $(COMPOSE_RUN) -e HOME="/tmp" node
YARN                 = $(COMPOSE_RUN_NODE) yarn

# ==============================================================================
# RULES

default: help

# -- Project

bootstrap: ## Prepare Docker images for the project
bootstrap: \
	env.d/development/crowdin \
	env.d/terraform \
  	env.d/development/aws \
	build \
	build-front \
	migrate
.PHONY: bootstrap

# -- Docker/compose
build: ## build the app container
	@$(COMPOSE) build ashley
.PHONY: build

down: ## stop and remove containers, networks, images, and volumes
	@$(COMPOSE) down
.PHONY: down

logs: ## display app logs (follow mode)
	@$(COMPOSE) logs -f ashley
.PHONY: logs

run: ## start the development server using Docker
	@$(COMPOSE) up -d
	@echo "Wait for postgresql to be up..."
	@$(WAIT_DB)
.PHONY: run

status: ## an alias for "docker-compose ps"
	@$(COMPOSE) ps
.PHONY: status

stop: ## stop the development server using Docker
	@$(COMPOSE) stop
.PHONY: stop

# -- Backend

# Nota bene: Black should come after isort just in case they don't agree...
lint: ## lint back-end python sources
lint: \
  lint-isort \
  lint-black \
  lint-flake8 \
  lint-mypy \
  lint-pylint \
  lint-bandit
.PHONY: lint

lint-bandit: ## lint back-end python sources with bandit
	@echo 'lint:bandit started…'
	@$(COMPOSE_TEST_RUN_APP) bandit -qr -x src/frontend src sandbox
.PHONY: lint-bandit

lint-black: ## lint back-end python sources with black
	@echo 'lint:black started…'
	@$(COMPOSE_TEST_RUN_APP) black src sandbox tests
.PHONY: lint-black

lint-flake8: ## lint back-end python sources with flake8
	@echo 'lint:flake8 started…'
	@$(COMPOSE_TEST_RUN_APP) flake8
.PHONY: lint-flake8

lint-isort: ## automatically re-arrange python imports in back-end code base
	@echo 'lint:isort started…'
	@$(COMPOSE_TEST_RUN_APP) isort --atomic .
.PHONY: lint-isort

lint-mypy: ## type check back-end python sources with mypy
	@echo 'lint:mypy started…'
	@$(COMPOSE_TEST_RUN_APP) mypy src/ashley
.PHONY: lint-mypy

lint-pylint: ## lint back-end python sources with pylint
	@echo 'lint:pylint started…'
	@$(COMPOSE_TEST_RUN_APP) pylint src sandbox tests
.PHONY: lint-pylint

test: ## run back-end tests
	bin/pytest
.PHONY: test

migrate:  ## run django migration for the ashley project.
	@echo "$(BOLD)Running migrations$(RESET)"
	@$(COMPOSE) up -d postgresql
	@$(WAIT_DB)
	@$(MANAGE) migrate
.PHONY: migrate

search-index: ## rebuild forum's index
	@echo "$(BOLD)Building index$(RESET)"
	@$(COMPOSE) up -d postgresql
	@$(WAIT_DB)
	@$(COMPOSE) up -d elasticsearch
	@$(WAIT_ES)
	@$(MANAGE) rebuild_index --noinput
.PHONY: search-index

superuser: ## create a Django superuser
	@echo "$(BOLD)Creating a Django superuser$(RESET)"
	@$(COMPOSE_RUN_APP) python sandbox/manage.py createsuperuser
.PHONY: superuser

# -- Frontend

build-front: ## build front-end application
build-front: \
	install-front \
	build-ts \
	build-sass \
	copy-webfonts
.PHONY: build-front

build-ts: ## build TypeScript application
	@$(YARN) compile-translations
	@$(YARN) build
.PHONY: build-ts

build-sass: ## build Sass files to CSS
	@$(YARN) sass
.PHONY: build-sass

copy-webfonts: ## Copy fonts to ashley static directory
	@$(YARN) webfonts

install-front: ## install front-end dependencies
	@$(YARN) install
.PHONY: install-front

lint-front: ## run all front-end "linters"
lint-front: \
  lint-front-tslint \
  lint-front-prettier
.PHONY: lint-front

lint-front-prettier: ## run prettier over js/jsx/json/ts/tsx files -- beware! overwrites files
	@$(YARN) prettier-write
.PHONY: lint-front-prettier

lint-front-tslint: ## lint TypeScript sources
	@$(YARN) lint-fix
.PHONY: lint-front-tslint

test-front: ## run front-end tests
	@$(YARN) test --runInBand
.PHONY: test-front

watch-sass: ## watch changes in Sass files
	@$(YARN) watch-sass
.PHONY: watch-sass

watch-ts: ## watch changes in TypeScript files
	@$(YARN) build --watch
.PHONY: watch-ts


# -- Internationalization

env.d/development/crowdin:
	cp env.d/development/crowdin.dist env.d/development/crowdin

crowdin-download: ## Download translated message from crowdin
	@$(COMPOSE_RUN_CROWDIN) download translations
.PHONY: crowdin-download

crowdin-upload: ## Upload source translations to crowdin
	@$(COMPOSE_RUN_CROWDIN) upload sources
.PHONY: crowdin-upload

i18n-extract-front:
	@$(YARN) extract-translations
.PHONY: i18n-extract-front

i18n-compile-front:
	@$(YARN) compile-translations
.PHONY: i18n-compile-front

i18n-compile-back : ## compile the gettext files
	@$(COMPOSE_RUN) -w /app/src/ashley ashley python /app/sandbox/manage.py compilemessages
.PHONY: i18n-compile-back

i18n-compile: \
  i18n-compile-back \
  i18n-compile-front
.PHONY: i18n-compile

i18n-download-and-compile: ## download all translated messages and compile them to be used by all applications
i18n-download-and-compile: \
  crowdin-download \
  i18n-compile
.PHONY: i18n-download-and-compile

i18n-generate-front: build-ts
	@$(YARN) extract-translations
.PHONY: i18n-generate-front

i18n-generate-back: ## create the .pot files used for i18n
	@$(COMPOSE_RUN) -w /app/src/ashley ashley python /app/sandbox/manage.py makemessages -a --keep-pot
	mv src/ashley/locale/django.pot src/ashley/locale/ashley.pot
	@$(COMPOSE_RUN) ashley bash -c 'msgfilter -i  $$(pip show -f django-machina 2>/dev/null | grep "Location:" | awk "{print \$$2}")"/machina/locale/en/LC_MESSAGES/django.po" -o /app/src/ashley/locale/machina.pot true'
	@$(COMPOSE_RUN) ashley msgcat --use-first /app/src/ashley/locale/machina.pot /app/src/ashley/locale/ashley.pot -o /app/src/ashley/locale/django.pot
	rm -f src/ashley/locale/ashley.pot
	rm -f src/ashley/locale/machina.pot
.PHONY: i18n-generate-back

i18n-generate: ## generate source translations files for all applications
i18n-generate: \
  i18n-generate-back \
  i18n-generate-front 
.PHONY: i18n-generate

i18n-generate-and-upload: ## generate source translations for all applications and upload them to crowdin
i18n-generate-and-upload: \
  i18n-generate \
  crowdin-upload
.PHONY: i18n-generate-and-upload

# -- Terraform

env.d/terraform:
	cp env.d/terraform.dist env.d/terraform

# -- Misc
help:
	@grep -E '^[a-zA-Z0-9_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
.PHONY: help

env.d/development/aws:## genererate personal setting file for aws
	cp env.d/development/aws.dist env.d/development/aws
	
sync-group-permission : ## synchronize groups with expected permissions
	@$(COMPOSE_RUN_APP) python sandbox/manage.py sync_group_permissions --apply
.PHONY: sync-group-permission
