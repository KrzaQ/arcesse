.PHONY: install uninstall docker-up docker-down

install:
	uv tool install -e .

uninstall:
	uv tool uninstall arcesse

docker-up:
	docker compose up -d

docker-down:
	docker compose down

-include Makefile.local
