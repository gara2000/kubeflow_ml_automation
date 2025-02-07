#### KIND CLUSTER CREATION ####
subsystem-changes:
	sudo sysctl fs.inotify.max_user_instances=2280
	sudo sysctl fs.inotify.max_user_watches=1255360
cluster:
	make subsystem-changes
	kind create cluster --name kubeflow --config kubeflow-kind-config.yaml
_cluster:
	kind delete cluster --name kubeflow
#### END OF KIND CLUSTER CREATION ####

#### METALLB ISNTALLATION ####
METALLB_DIR=metallb
metallb_:
	kubectl apply -f https://raw.githubusercontent.com/metallb/metallb/v0.14.8/config/manifests/metallb-native.yaml
	cd $(METALLB_DIR) && kubectl apply -f ip-range.yaml
	cd $(METALLB_DIR) && kubectl apply -f l2advertisement.yaml
#### END OF METALLB ISNTALLATION ####

#### KUBEFLOW PLATFORM INSTALLATION ####
MANIFESTS_DIR=manifests
manifests:
	git clone https://github.com/kubeflow/manifests.git
kubeflow:
	cd $(MANIFESTS_DIR) ; kustomize build example | kubectl apply -f -
manifests_:
	rm -rf manifests/
build-kubeflow:
	make manifests_
	make manifests
	while ! make kubeflow ; do echo "Retrying to apply resources..." ; sleep 20 ; done
expose-kubeflow:
	kubectl port-forward svc/istio-ingressgateway -n istio-system 8080:80
kserve-server-side-forcing:
	cd $(MANIFESTS_DIR) && while ! kustomize build contrib/kserve/kserve | kubectl apply --server-side --force-conflicts -f - ; do echo "Retrying..." ; sleep 20 ; done	
kubeflow-metallb: 
	while ! make metallb_ ; do echo "Retrying..." ; sleep 10 ; done
#### END OF KUBEFLOW PLATFORM INSTALLATION ####

#### PROMETHEUS AND GRAFANA INSTALLATION ####
prometheus:
	helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
	helm repo update
	helm install prometheus prometheus-community/prometheus --namespace monitoring --create-namespace
grafana:
	helm repo add grafana https://grafana.github.io/helm-charts
	helm repo update
	helm install grafana grafana/grafana --namespace monitoring --create-namespace --set persistence.enabled=true --set persistence.size=10Gi
prometheus-expose:
	kubectl port-forward svc/prometheus-server -n monitoring 9090:80
	# export POD_NAME=$(kubectl get pods --namespace monitoring -l "app=prometheus-pushgateway,component=pushgateway" -o jsonpath="{.items[0].metadata.name}")
	# kubectl --namespace monitoring port-forward $(POD_NAME) 9091
grafana-expose:
	kubectl port-forward svc/grafana -n monitoring 3000:80
	# export POD_NAME=$(kubectl get pods --namespace monitoring -l "app.kubernetes.io/name=grafana,app.kubernetes.io/instance=grafana" -o jsonpath="{.items[0].metadata.name}")
	# kubectl --namespace monitoring port-forward $(POD_NAME) 8000:3000
grafana-admin-password:
	@kubectl get secret --namespace monitoring grafana -o jsonpath="{.data.admin-password}" | base64 --decode ; echo
#### END OF PROMETHEUS AND GRAFANA INSTALLATION ####

#### KFP STANDALONE INSTALLATION #####
PIPELINE_VERSION=1.3.0
kfp_standalone:
ifndef PIPELINE_VERSION
        @echo "Error: env var PIPELINE_VERSION is not set. Please set it and try again." >&2
        @exit 1
endif
	kubectl apply -k "github.com/kubeflow/pipelines/manifests/kustomize/cluster-scoped-resources?ref=$(PIPELINE_VERSION)"
	kubectl wait --for condition=established --timeout=60s crd/applications.app.k8s.io
	kubectl apply -k "github.com/kubeflow/pipelines/manifests/kustomize/env/dev?ref=$(PIPELINE_VERSION)"
#### KFP STANDALONE INSTALLATION #####

#### DEPLOY MODEL REGISTRY #####
REGISTRY_BUILD_DIR='manifests/apps/model-registry/upstream'
NAMESPACE=kubeflow-user-example-com
model-registry:
	cd $(REGISTRY_BUILD_DIR) && kubectl apply  -k overlays/db
	cd $(REGISTRY_BUILD_DIR) && kubectl apply  -k options/istio
	cd $(REGISTRY_BUILD_DIR) && kubectl apply  -k options/csi

	# Install remotely 
	# kubectl apply -k "https://github.com/kubeflow/model-registry/manifests/kustomize/overlays/db?ref=v0.2.10"
	# kubectl apply -k "https://github.com/kubeflow/model-registry/manifests/kustomize/options/istio?ref=v0.2.10"
	# kubectl apply -k "https://github.com/kubeflow/model-registry/manifests/kustomize/options/csi?ref=v0.2.10"

	kubectl wait --for=condition=available -n kubeflow deployment/model-registry-deployment --timeout=2m
	kubectl logs -n kubeflow deployment/model-registry-deployment
_model-registry:
	- cd $(REGISTRY_BUILD_DIR) && kubectl delete -k options/istio
	- cd $(REGISTRY_BUILD_DIR) && kubectl delete -k overlays/db
model-registry-expose:
	kubectl port-forward svc/model-registry-service -n kubeflow 8081:8080
#### END OF DEPLOY MODEL REGISTRY #####

#### MINIO #####
minio-expose:
	kubectl port-forward -n kubeflow svc/minio-service 9000:9000
minio-access-secrets:
	@kubectl get secret -n kubeflow-user-example-com mlpipeline-minio-artifact -o jsonpath="{.data.accesskey}" | base64 --decode
	@echo
	@kubectl get secret -n kubeflow-user-example-com mlpipeline-minio-artifact -o jsonpath="{.data.secretkey}" | base64 --decode
#### END OF MINIO #####

#### GENERAL UTILS #####
watch_pods:
	kubectl get pods -n kubeflow-user-example-com -w
delete_succeeded_pods:
	kubectl delete pods -n kubeflow-user-example-com --field-selector status.phase==Succeeded
delete_failed_pods:
	kubectl delete pods -n kubeflow-user-example-com --field-selector status.phase==Failed
clean_pods: delete_failed_pods delete_succeeded_pods
#### END OF GENERAL UTILS #####

#### THE ORDER OF MAKE COMMANDS TO LAUNCH EVERYTHING ####
# KIND CLUSTER
launch_cluster: cluster
# KUBEFLOW
launch_kubeflow: build-kubeflow
launch_kserve: kserve-server-side-forcing
# MODEL REGISTRY
launch_model_registry: model-registry
# PROMETHEUS
launch_prometheus: prometheus
# GRAFANA
launch_grafana: grafana
# SHOW KUBEFLOW DASHBOARD
expose_kubeflow: expose-kubeflow
# SHOW GRAFANA DASHBOARD
expose_grafana: grafana-expose
# EXPOSE MODEL REGSITRY SERVICE
expose_model-registry: model-registry-expose
