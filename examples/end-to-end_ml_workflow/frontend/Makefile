APP_DIR=application
DEP_DIR=deployments
SVC_DIR=services
UI_VERSION=1.0.3
build-ui:
	cd $(APP_DIR) && docker build -t 2cassa2/kserve-frontend-ui:$(UI_VERSION) .
push-ui-image:
	docker push 2cassa2/kserve-frontend-ui:$(UI_VERSION)
deploy-ui:
	cd $(DEP_DIR) && kubectl apply -f frontend.yaml
	cd $(SVC_DIR) && kubectl apply -f frontend.yaml
	kubectl apply -f external-access-to-frontend.yaml
	kubectl apply -f access-frontend-isvc.yaml
delete-ui:
	- cd $(DEP_DIR) && kubectl delete -f frontend.yaml
	- cd $(SVC_DIR) && kubectl delete -f frontend.yaml
	- kubectl delete -f external-access-to-frontend.yaml
	- kubectl delete -f access-frontend-isvc.yaml

all: delete-ui build-ui push-ui-image deploy-ui
