import kfp
from kfp.v2.dsl import component, Output, Dataset, Input

@component(
    base_image="2cassa2/kfp-runtime:1.0.0",
    packages_to_install=["kubernetes==31.0.0"]
)
def model_upload(
    model_dir: Input[Dataset],
    original_model_name: str,
    secret_name: str,
    secret_namespace: str
):
    from kubernetes import client, config

    # Load in-cluster Kubernetes config
    config.load_incluster_config()

    # Access the Kubernetes CoreV1API
    v1 = client.CoreV1Api()

    # Retrieve the secret
    secret = v1.read_namespaced_secret(name=secret_name, namespace=secret_namespace)
    hf_repo = secret.data["repo"]
    hf_token = secret.data["token"]
    # Decode the secret values (Kubernetes secrets are base64-encoded)
    import base64
    hf_repo = base64.b64decode(hf_repo).decode("utf-8")
    hf_token = base64.b64decode(hf_token).decode("utf-8")

    from huggingface_hub import login
    from transformers import AutoTokenizer, AutoModelForCausalLM
    
    # Login to Hugging Face
    login(hf_token)
    
    # Push model and tokenizer
    model = AutoModelForCausalLM.from_pretrained(model_dir.path)
    tokenizer = AutoTokenizer.from_pretrained(original_model_name)
    
    model.push_to_hub(hf_repo)
    tokenizer.push_to_hub(hf_repo)
