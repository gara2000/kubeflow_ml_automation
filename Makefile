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
metallb:
	kubectl apply -f https://raw.githubusercontent.com/metallb/metallb/v0.14.8/config/manifests/metallb-native.yaml
	cd $(KSERVE_DIR) && kubectl apply -f ip-range.yaml
	cd $(KSERVE_DIR) && kubectl apply -f l2advertisement.yaml
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
	make manifests_
expose-kubeflow:
	kubectl port-forward svc/istio-ingressgateway -n istio-system 8080:80
kserve-server-side-forcing:
	cd $(MANIFESTS_DIR) && while ! kustomize build contrib/kserve/kserve | kubectl apply --server-side --force-conflicts -f - ; do echo "Retrying..." ; sleep 20 ; done	
kubeflow-metallb: 
	while ! make metallb ; do echo "Retrying..." ; sleep 10 ; done
#### END OF KUBEFLOW PLATFORM INSTALLATION ####

#### PROMETHEUS AND GRAFANA INSTALLATION ####
prometheus:
	helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
	helm repo update
	helm install prometheus prometheus-community/prometheus --namespace monitoring --create-namespace
grafana:
	helm repo add grafana https://grafana.github.io/helm-charts
	helm repo update
	helm install grafana grafana/grafana --namespace monitoring --create-namespace
prometheus-expose:
	kubectl port-forward svc/prometheus-server -n monitoring 9090:80
grafana-expose:
	kubectl port-forward svc/grafana -n monitoring 3000:3000
#### END OF PROMETHEUS AND GRAFANA INSTALLATION ####
