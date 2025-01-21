DOCKERHUB_USERNAME=2cassa2
APP_NAME=text-generation-api
VERSION=0.0.1
IMAGE_NAME=$(DOCKERHUB_USERNAME)/$(APP_NAME):$(VERSION)
CONTAINER_NAME=test-endpoint
build:
	docker build -t $(IMAGE_NAME) .
run-test:
ifndef HF_TOKEN
	@echo "Error: env var HF_TOKEN is not set. Please set it and try again." >&2
	@exit 1
endif
ifndef LANGCHAIN_TRACING_V2
	@echo "Error: env var LANGCHAIN_TRACING_V2 is not set. Please set it and try again." >&2
	@exit 1
endif
ifndef LANGCHAIN_ENDPOINT
	@echo "Error: env var LANGCHAIN_ENDPOINT is not set. Please set it and try again." >&2
	@exit 1
endif
ifndef LANGCHAIN_API_KEY
	@echo "Error: env var LANGCHAIN_API_KEY is not set. Please set it and try again." >&2
	@exit 1
endif
ifndef LANGCHAIN_PROJECT
	@echo "Error: env var LANGCHAIN_PROJECT is not set. Please set it and try again." >&2
	@exit 1
endif
	docker run --rm -it --name $(CONTAINER_NAME) \
	 -p 5000:5000 \
	 -e MODEL_NAME="microsoft/Phi-3-mini-4k-instruct" \
	 -e HF_TOKEN=$(HF_TOKEN) \
	 -e LANGCHAIN_TRACING_V2=$(LANGCHAIN_TRACING_V2) \
	 -e LANGCHAIN_ENDPOINT=$(LANGCHAIN_ENDPOINT) \
	 -e LANGCHAIN_API_KEY=$(LANGCHAIN_API_KEY) \
	 -e LANGCHAIN_PROJECT=$(LANGCHAIN_PROJECT) \
	$(IMAGE_NAME)	
login:
ifndef DOCKERHUB_TOKEN
	@echo "Error: env var DOCKERHUB_TOKEN is not set. Please set it and try again." >&2
	@exit 1
endif
	echo $(DOCKERHUB_TOKEN) | docker login -u $(DOCKERHUB_USERNAME) --password-stdin
push:
	docker push $(IMAGE_NAME)