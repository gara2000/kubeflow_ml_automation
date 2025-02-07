IMAGE_NAME=2cassa2/hey:1.0.0
DOCKERHUB_USERNAME=2cassa2
build:
	docker build -t $(IMAGE_NAME) .
login:
ifndef DOCKERHUB_TOKEN
	@echo "Error: env var DOCKERHUB_TOKEN is not set. Please set it and try again." >&2
	@exit 1
endif
	echo $(DOCKERHUB_TOKEN) | docker login -u $(DOCKERHUB_USERNAME) --password-stdin
push:
	docker push $(IMAGE_NAME)

