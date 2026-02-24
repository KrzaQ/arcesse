.PHONY: install uninstall docker-build docker-up docker-up-all docker-down

install:
	uv tool install --force -e .

uninstall:
	uv tool uninstall arcesse

docker-build:
	docker compose build camoufox

docker-up:
	docker compose up -d

docker-up-all:
	docker compose --profile flaresolverr --profile byparr up -d

docker-down:
	docker compose --profile flaresolverr --profile byparr down

-include Makefile.local
