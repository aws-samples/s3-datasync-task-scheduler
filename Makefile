dev:
	trap 'kill %1' SIGINT
	sam local start-api

infra:
	./infrastructure/deploy.sh