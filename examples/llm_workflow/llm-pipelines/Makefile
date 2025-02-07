HF_REPO?="cassa20/llmops_ft_bert"
create-secret:
ifndef HF_TOKEN
	@echo "Error: env var HF_TOKEN is not set. Please set it and try again." >&2
	@exit 1
endif
	kubectl create secret generic huggingface-secret \
	--namespace=kubeflow-user-example-com \
	--from-literal=token=$(HF_TOKEN) \
	--from-literal=repo=$(HF_REPO)
