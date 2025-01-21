from kfp.v2.dsl import pipeline
from .components.dataFetcher import data_fetching
from .components.tokenizer import data_tokenization
from .components.finetuning import model_fine_tuning
from .components.modelUpload import model_upload

@pipeline(name="huggingface-model-pipeline")
def pipeline(
    # huggingface_repo_name: str,
    # huggingface_token: str,
    api_docker_image: str = "2cassa2/finetuned-llm-api",
    dataset_name: str = "yelp_review_full",
    dataset_text_column: str = "text",
    model_name: str = "google-bert/bert-base-cased",
    max_length: int = 128,
    model_repo: str = "cassa20/llmops_ft_bert"
    # epochs: int = 3
):
    # Step 1: Data Fetching
    # dataset_name = "openwebtext"
    fetch_data = data_fetching(
        dataset_name=dataset_name,
        splits=[
            {
            "split_name": "train",
            "split_size": 1000
            },
            {
            "split_name": "test",
            "split_size": 1000
            }
        ]
    )
    # Step 2: Data Tokenization
    tokenize_data = data_tokenization(
        input_dataset=fetch_data.outputs["output_dataset"],
        dataset_text_column=dataset_text_column,
        model_name=model_name,
    )
    
    # Step 3: Model Fine-Tuning
    fine_tune = model_fine_tuning(
        tokenized_data=tokenize_data.outputs["output_dataset"],
        model_name=model_name,
    )
    
    # Step 4: Model Upload
    upload_model = model_upload(
        model_dir=fine_tune.outputs["output_model_dir"],
        original_model_name=model_name,
        secret_name="huggingface-secret",
        secret_namespace="kubeflow-user-example-com" 
    )
    
    # # Step 5: Docker Deployment
    docker_deployment(
        model_name="finetuned_bert",
        model_path=model_repo, # build a config map for the model path
        docker_image=api_docker_image, # build an inference service for the api
        namespace="kubeflow-user-example-com"
    )

from .kfpclientmanager import KFPClientManager

# initialize a KFPClientManager
kfp_client_manager = KFPClientManager(
    api_url="http://localhost:8080/pipeline",
    skip_tls_verify=True,

    dex_username="user@example.com",
    dex_password="12341234",

    # can be 'ldap' or 'local' depending on your Dex configuration
    dex_auth_type="local",
)

# get a newly authenticated KFP client
# TIP: long-lived sessions might need to get a new client when their session expires
kfp_client = kfp_client_manager.create_kfp_client()

# test the client by listing experiments
# experiments = kfp_client.list_experiments(namespace="kubeflow-user-example-com")
# print(experiments)
run = kfp_client.create_run_from_pipeline_func(
    pipeline,
    namespace="kubeflow-user-example-com",
    # enable_caching=False,
    arguments={
        # huggingface_repo_name: "",
        # huggingface_token: "",
        # docker_image: "",
        "dataset_name" : "yelp_review_full",
        "dataset_text_column" : "text",
        "model_name" : "google-bert/bert-base-cased",
        "max_length" : 128
    },
)