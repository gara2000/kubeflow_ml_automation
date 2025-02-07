IMAGE_NAME=2cassa2/ad_inference_endpoint:1.0.0
MINIO_ENDPOINT = "http://localhost:9000"
MINIO_ACCESS_KEY = "minio"
MINIO_SECRET_KEY = "minio123"
MODEL_NAME="RandomForestClassifier_for_AD"
MODEL_VERSION="v1.0.1"
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

rebuild: build push