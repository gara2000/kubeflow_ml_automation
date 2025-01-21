VERSION=0.0.1
REPO_NAME=llm-streamlit-ui
DOCKERHUB_USERNAME=2cassa2
IMAGE_NAME=$(DOCKERHUB_USERNAME)/$(REPO_NAME):$(VERSION)
TEST_CONTAINER_NAME="test-llm-ui"
PORT=8501
build:
	docker build -t $(IMAGE_NAME) .
run-test:
ifndef API_URL
	@echo "Error: env var API_URL is not set. Please set it and try again." >&2
	@exit 1
endif
	docker run -ti --rm \
		-p $(PORT):$(PORT) \
		-e API_URL=$(API_URL) \
		$(IMAGE_NAME)
login:
ifndef DOCKERHUB_TOKEN
	@echo "Error: env var DOCKERHUB_TOKEN is not set. Please set it and try again." >&2
	@exit 1
endif
	echo $(DOCKERHUB_TOKEN) | docker login -u $(DOCKERHUB_USERNAME) --password-stdin
push:
	docker push $(IMAGE_NAME)