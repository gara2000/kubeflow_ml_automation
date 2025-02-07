from typing import List

from kfp import client
from kfp import dsl
from kfp.dsl import Input, Output, Dataset, Model
from kfp import compiler
import os

current_dir = os.path.dirname(os.path.abspath(__file__))

@dsl.component(packages_to_install=['pandas==1.3.5', 'numpy==1.20.3'])
def create_dataset(iris_dataset: Output[Dataset]):
    import pandas as pd

    csv_url = 'https://archive.ics.uci.edu/ml/machine-learning-databases/iris/iris.data'
    col_names = [
        'Sepal_Length', 'Sepal_Width', 'Petal_Length', 'Petal_Width', 'Labels'
    ]
    df = pd.read_csv(csv_url, names=col_names)

    with open(iris_dataset.path, 'w') as f:
        df.to_csv(f)


@dsl.component(packages_to_install=['pandas==1.3.5', 'scikit-learn==1.0.2', 'numpy==1.20.3'])
def normalize_dataset(
    input_iris_dataset: Input[Dataset],
    normalized_iris_dataset: Output[Dataset],
    standard_scaler: bool,
    min_max_scaler: bool,
):
    if standard_scaler is min_max_scaler:
        raise ValueError(
            'Exactly one of standard_scaler or min_max_scaler must be True.')

    import pandas as pd
    from sklearn.preprocessing import MinMaxScaler
    from sklearn.preprocessing import StandardScaler

    with open(input_iris_dataset.path) as f:
        df = pd.read_csv(f)
    labels = df.pop('Labels')

    if standard_scaler:
        scaler = StandardScaler()
    if min_max_scaler:
        scaler = MinMaxScaler()

    df = pd.DataFrame(scaler.fit_transform(df))
    df['Labels'] = labels
    with open(normalized_iris_dataset.path, 'w') as f:
        df.to_csv(f)

@dsl.component(packages_to_install=['scikit-learn', 'joblib', 'pandas'])
def train_model(data: Input[Dataset], model: Output[Model]):
    import joblib
    import pandas as pd
    from sklearn.ensemble import RandomForestClassifier

    with open(data.path) as f:
        df = pd.read_csv(f)
    y = df.pop('Labels')
    X = df
    clf = RandomForestClassifier()
    clf.fit(X, y)

    # Save the model to the output path
    joblib.dump(clf, model.path)

@dsl.component(packages_to_install=["kubernetes"])
def deploy_model(
    model: Input[Model],  # The model to deploy
    inference_service_name: str,  # Name for the KServe InferenceService
    namespace: str = "default",  # Namespace to deploy the service
):
    from kubernetes import client, config

    # Load Kubernetes configuration
    config.load_incluster_config()  # Use in-cluster config for the pipeline
    api_instance = client.CustomObjectsApi()

    # Define the KServe InferenceService YAML
    inference_service = {
        "apiVersion": "serving.kserve.io/v1beta1",
        "kind": "InferenceService",
        "metadata": {
            "name": inference_service_name,
            "namespace": namespace,
        },
        "spec": {
            "predictor": {
                "model": {
                    "modelFormat": {
                        "name": "sklearn",
                    }, 
                    "storageUri": model.path,
                }
            }
        },
    }

    # Deploy the InferenceService
    api_instance.create_namespaced_custom_object(
        group="serving.kserve.io",
        version="v1beta1",
        namespace=namespace,
        plural="inferenceservices",
        body=inference_service,
    )
    print(f"InferenceService {inference_service_name} deployed in namespace {namespace}.")

@dsl.pipeline(name='model-training-pipeline')
def pipeline(
    standard_scaler: bool,
    min_max_scaler: bool
):
    create_dataset_task = create_dataset()

    normalize_dataset_task = normalize_dataset(
        input_iris_dataset=create_dataset_task.outputs['iris_dataset'],
        standard_scaler=True,
        min_max_scaler=False)

    train_task = train_model(
        data=normalize_dataset_task.outputs['normalized_iris_dataset']
    )

    deploy_task = deploy_model(
        model=train_task.outputs['model'],
        inference_service_name="sklearn-model",
        namespace="kubeflow-user-example-com"
    )

    # train_task.add_volume(
    #     kubernetes.client.V1Volume(
    #         name="model-storage-pv",
    #         persistent_volume_claim=kubernetes.client.V1PersistentVolumeClaimVolumeSource(
    #             claim_name="model-storage-pvc"
    #         )
    #     )
    # ).add_volume_mount(
    #     kubernetes.client.V1VolumeMount(
    #         name="model-storage-pv",
    #         mount_path="/mnt/kserve-models"
    #     )
    # )

# compiler.Compiler().compile(pipeline, f'{current_dir}/pipeline.yaml')

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
        'min_max_scaler': True,
        'standard_scaler': False
    },
)