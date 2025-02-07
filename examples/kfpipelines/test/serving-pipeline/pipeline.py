from kfp import dsl

@dsl.component(packages_to_install=["kubernetes"])
def create_inference_service(
    model_name: str,
    docker_image: str,
    namespace: str = "kubeflow-user-example-com",
):
    """
    Creates a KServe InferenceService in the specified namespace using the Kubernetes client.
    
    Args:
        model_name (str): Name of the InferenceService.
        docker_image (str): DockerHub image for the inference service.
        namespace (str): Namespace in which the service will be deployed.
    """
    from kubernetes import client, config
    # Load the in-cluster Kubernetes configuration
    config.load_incluster_config()

    # Create the KServe InferenceService resource
    inference_service = {
        "apiVersion": "serving.kserve.io/v1beta1",
        "kind": "InferenceService",
        "metadata": {
            "name": model_name,
            "namespace": namespace,
            "labels": {
                "app": "inferenceservice",
            },
        },
        "spec": {
            "predictor": {
                "containers": [
                    {
                        "name": "kserve-container",
                        "image": docker_image,
                        "ports": [
                            {"containerPort": 8080},
                        ],
                    }
                ]
            }
        },
    }

    # Use the Kubernetes client to create the InferenceService
    api_instance = client.CustomObjectsApi()
    group = "serving.kserve.io"
    version = "v1beta1"
    plural = "inferenceservices"

    try:
        api_instance.create_namespaced_custom_object(
            group=group,
            version=version,
            namespace=namespace,
            plural=plural,
            body=inference_service,
        )
        print(f"InferenceService '{model_name}' created successfully in namespace '{namespace}'.")
    except client.exceptions.ApiException as e:
        print(f"Exception when creating InferenceService: {e}")
        raise

@dsl.pipeline(
    name="KServe Inference Pipeline",
    description="Pipeline to deploy a KServe InferenceService using in-cluster Kubernetes config."
)
def pipeline():
    # Parameters
    model_name = "sklearn-model"
    docker_image = "2cassa2/llmops-test-model:1.0.0"
    namespace = "kubeflow-user-example-com"

    # Call the component
    create_inference_service(
        model_name=model_name,
        docker_image=docker_image,
        namespace=namespace,
    )

from ..kfpclientmanager import KFPClientManager

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
    arguments={
    },
)