from kfp import client, dsl
from kubernetes.client.models import V1EnvVar, V1EnvVarSource, V1SecretKeySelector
from .components.data_engineering import create_dataset, normalize_dataset
from .components.serving import create_inference_service
from .components.training_beta import train_push_model

@dsl.pipeline(name='model-training-pipeline')
def pipeline(
    standard_scaler: bool,
    min_max_scaler: bool
):

    train_push_task = train_push_model(
        github_repo_url='https://github.com/gara2000/llmops_model_api.git',
    )
    train_push_task.set_caching_options(False) 
    ## Think of deviding the train_push_task into 2 separate tasks:
    ## # train_task that can use cache
    ## # push_task that shouldn't use cache (it should always push to github)

    deploy_task = create_inference_service(
        docker_image="2cassa2/llmops-test-model:1.0.3",
        model_name="sklearn-model",
        namespace="kubeflow-user-example-com"
    ).after(train_push_task)
    deploy_task.set_caching_options(False)

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
        'min_max_scaler': True,
        'standard_scaler': False
    },
)