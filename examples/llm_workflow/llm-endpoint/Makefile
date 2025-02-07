UI_FILE=llm-ui.yaml
API_FILE=llm-api.yaml
# LANGCHAIN_PROJECT=kubeflow
api-deploy:	
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
	kubectl apply -f k8s/configmaps/$(API_FILE)
	kubectl apply -f k8s/inference-services/$(API_FILE)
	kubectl apply -f k8s/authorization-policies/$(API_FILE)
	kubectl create secret -n kubeflow-user-example-com generic llm-api-secret\
		--from-literal=hf_token=$(HF_TOKEN)\
		--from-literal=langchain_tracing_v2=$(LANGCHAIN_TRACING_V2)\
		--from-literal=langchain_api_key=$(LANGCHAIN_API_KEY)\
		--from-literal=langchain_project=$(LANGCHAIN_PROJECT)\
		--from-literal=langchain_endpoint=$(LANGCHAIN_ENDPOINT)\
		--from-literal=tavily_api_key=$(TAVILY_API_KEY)
api-destroy:
	- kubectl delete -f k8s/authorization-policies/$(API_FILE)
	- kubectl delete -f k8s/inference-services/$(API_FILE)
	- kubectl delete -f k8s/configmaps/$(API_FILE)
	- kubectl delete secret -n kubeflow-user-example-com llm-api-secret
ui-deploy:
	kubectl apply -f k8s/configmaps/$(UI_FILE)
	kubectl apply -f k8s/services/$(UI_FILE)
	kubectl apply -f k8s/deployments/$(UI_FILE)
	kubectl apply -f k8s/authorization-policies/$(UI_FILE)
ui-destroy:
	- kubectl delete -f k8s/configmaps/$(UI_FILE)
	- kubectl delete -f k8s/services/$(UI_FILE)
	- kubectl delete -f k8s/deployments/$(UI_FILE)
	- kubectl delete -f k8s/authorization-policies/$(UI_FILE)

