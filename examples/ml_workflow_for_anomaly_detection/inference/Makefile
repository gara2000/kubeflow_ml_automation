configmap:
	kubectl apply -f configmap.yaml
_configmap:
	kubectl delete -f configmap.yaml
inference:
	kubectl apply -f inferenceservice.yaml
_inference:
	kubectl delete -f inferenceservice.yaml
start: configmap inference
stop: _inference _configmap

	
