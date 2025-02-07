inference:
	kubectl apply -f inference.yaml
	kubectl get pods
	kubectl get isvc

AUTOSCALING=autoscaling
test-autoscaling:
	cd $(AUTOSCALING) && kubectl apply -f configmap.yaml
	cd $(AUTOSCALING) && kubectl apply -f job.yaml
_test_autoscaling:
	- cd $(AUTOSCALING) && kubectl delete -f configmap.yaml
	- cd $(AUTOSCALING) && kubectl delete -f job.yaml
