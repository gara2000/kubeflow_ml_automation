from kfp import dsl

@dsl.component(packages_to_install=["kubernetes==31.0.0"])
def create_inference_service(
    model_name: str,
    model_repo: str,
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

    # Create a ConfigMap to store the MODEL_NAME
    config_map_name = f"{model_name}-configmap"
    config_map = client.V1ConfigMap(
        metadata=client.V1ObjectMeta(
            name=config_map_name,
            namespace=namespace,
        ),
        data={
            "MODEL_NAME": model_repo,
        },
    )

    # Use the Kubernetes client to create the ConfigMap
    core_api_instance = client.CoreV1Api()
    try:
        core_api_instance.create_namespaced_config_map(
            namespace=namespace, body=config_map
        )
        print(f"ConfigMap '{config_map_name}' created successfully in namespace '{namespace}'.")
    except client.exceptions.ApiException as e:
        print(f"Exception when creating ConfigMap: {e}")
        raise

    # Create the KServe InferenceService resource with the environment variable
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
                        "env": [
                            {
                                "name": "MODEL_NAME",
                                "valueFrom": {
                                    "configMapKeyRef": {
                                        "name": config_map_name,
                                        "key": "MODEL_NAME",
                                    }
                                },
                            }
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