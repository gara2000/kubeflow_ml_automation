USER=2cassa2
REPO=kfp-runtime
VERSION=1.0.0
IMAGE=$(USER)/$(REPO):$(VERSION)
build:
	docker build -t $(IMAGE) .
run-test:
	docker run --rm -dit --name test-runtime $(IMAGE)
	docker exec -ti test-runtime /bin/bash
destroy-test:
	docker rm -f test-runtime
login:
ifndef DOCKERHUB_TOKEN
	@echo "Error: env var DOCKERHUB_TOKEN is not set. Please set it and try again." >&2
	@exit 1
endif
	echo $(DOCKERHUB_TOKEN) | docker login -u $(USER) --password-stdin
push:
	docker push $(IMAGE)
