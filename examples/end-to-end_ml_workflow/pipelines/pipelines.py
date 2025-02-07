from typing import List

from kfp import client
from kfp import dsl
from kfp.dsl import Dataset
from kfp.dsl import Input
from kfp.dsl import Model
from kfp.dsl import Output
from kfp import kubernetes

@dsl.component(packages_to_install=['scikit-learn==1.5.2', 'pandas==2.2.3', 'numpy==2.0.2'])
def create_dataset(iris_dataset: Output[Dataset]):
    import pandas as pd

    csv_url = 'https://archive.ics.uci.edu/ml/machine-learning-databases/iris/iris.data'
    col_names = [
        'Sepal_Length', 'Sepal_Width', 'Petal_Length', 'Petal_Width', 'Labels'
    ]
    df = pd.read_csv(csv_url, names=col_names)

    with open(iris_dataset.path, 'w') as f:
        df.to_csv(f, index=False)

@dsl.component(packages_to_install=['scikit-learn==1.5.2', 'pandas==2.2.3', 'numpy==2.0.2'])
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
        df.to_csv(f, index=False)


@dsl.component(packages_to_install=['scikit-learn==1.5.2', 'pandas==2.2.3', 'numpy==2.0.2', 'model_registry==0.2.10'])
def train_model(
    model_name: str,
    version: str,
    normalized_iris_dataset: Input[Dataset],
    n_neighbors: int,
    model: Output[Model],
):
    import pickle
    import os

    import pandas as pd
    from sklearn.model_selection import train_test_split
    from sklearn.neighbors import KNeighborsClassifier
    from sklearn.metrics import accuracy_score

    with open(normalized_iris_dataset.path) as f:
        df = pd.read_csv(f)

    y = df.pop('Labels')
    X = df

    X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=0)

    clf = KNeighborsClassifier(n_neighbors=n_neighbors)
    clf.fit(X_train, y_train)
    y_pred = clf.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)

    model_name = model_name+f"_{n_neighbors}"
    folder_path = f"{model.path}/{model_name.lower()}/{version}"
    os.makedirs(folder_path, exist_ok=True)
    model_path = f"{model.path}/{model_name.lower()}/{version}/model.pickle"
    model_uri= f"{model.uri}/{model_name.lower()}/{version}/model.pickle"
    with open(model_path, "wb") as f:
        pickle.dump(clf, f)
    print(f"Model saved to {model_path}")

    model.metadata["path"] = model_path
    print(model_path)

    from model_registry import ModelRegistry

    registry = ModelRegistry(
        server_address="http://model-registry-service.kubeflow.svc.cluster.local",
        port=8080,
        author="Cassa",
        is_secure=False
    )

    try:
        rm = registry.register_model(
            model_name,
            model_uri,
            model_format_name="sklearn",
            model_format_version="1",
            version=version,
            description=f"{model_name}",
            metadata={
                "accuracy": float(accuracy)
            }
        )
    except Exception as e:
        print(f"Error when registering the model: {e}")



@dsl.component(packages_to_install=['scikit-learn==1.5.2', 'pandas==2.2.3', 'numpy==2.0.2', 'model_registry==0.2.10', 'boto3==1.36.11'])
def best_model(
    model_version: str,
):
    import pickle
    import os
    from model_registry import ModelRegistry
    import sklearn
    import boto3

    registry = ModelRegistry(
        server_address="http://model-registry-service.kubeflow.svc.cluster.local",
        port=8080,
        author="Cassa",
        is_secure=False
    )    
    
    print("Hello, entered registry!")
    best_metric_value = 0 # The metric should be ascending 
    metric_name = "accuracy"
    for curr_model in registry.get_registered_models():
        curr_version = registry.get_model_version(curr_model.name, model_version)
        curr_metric = curr_version.custom_properties.get(metric_name, '0')
        if curr_metric >= best_metric_value:
            model_name = curr_model.name
            model = curr_model
            version = curr_version 
            best_metric_value = curr_metric
        print(f"{model.name} has {metric_name} of : {curr_metric}")

    print("Registered Model:", model, "with ID", model.id)
    print("Model Version:", version, "with ID", version.id)
    art = registry.get_model_artifact(model_name, model_version)
    print("Model Artifact:", art, "with ID", art.id)

    MINIO_ENDPOINT="http://minio-service.kubeflow.svc.cluster.local:9000"
    MINIO_ACCESS_KEY="minio"
    MINIO_SECRET_KEY="minio123"
    s3_client = boto3.client(
        "s3",
        endpoint_url=MINIO_ENDPOINT,
        aws_access_key_id=MINIO_ACCESS_KEY,
        aws_secret_access_key=MINIO_SECRET_KEY,
    )
    uri = art.uri
    # print("URI: ", uri)
    MINIO_BUCKET = uri.split("minio://")[-1].split('/')[0]
    # print("MINIO_BUCKET: ", MINIO_BUCKET, "\n")
    MINIO_OBJECT_KEY = uri.split(MINIO_BUCKET)[-1][1:]
    # MINIO_OBJECT_KEY = uri.split(uri)[-1][1:]
    LOCAL_MODEL_PATH = f"/data/models/{model_name}/{model_version}/model/model.pkl"
    LOCAL_MODEL_DIR = f"/data/models/{model_name}/{model_version}/model"
    os.makedirs(LOCAL_MODEL_DIR, exist_ok=True)
    print("MODEL DIRECTORY: ", os.listdir(LOCAL_MODEL_DIR))
    print(f"File path: {MINIO_OBJECT_KEY}")
    try:
        # Download the object from MinIO
        s3_client.download_file(MINIO_BUCKET, MINIO_OBJECT_KEY, LOCAL_MODEL_PATH)
        print(f"Model downloaded successfully and saved to {LOCAL_MODEL_PATH}")
    except Exception as e:
        print(f"Error downloading the model: {str(e)}")

@dsl.pipeline(name='iris-training-pipeline')
def training_pipeline(
    standard_scaler: bool,
    min_max_scaler: bool,
    neighbors: List[int],
):
    create_dataset_task = create_dataset()

    normalize_dataset_task = normalize_dataset(
        input_iris_dataset=create_dataset_task.outputs['iris_dataset'],
        standard_scaler=True,
        min_max_scaler=False)

    with dsl.ParallelFor(neighbors) as n_neighbors:
        train_model_task = train_model(
            model_name="KNN",
            version="v1",
            normalized_iris_dataset=normalize_dataset_task
            .outputs['normalized_iris_dataset'],
            n_neighbors=n_neighbors)

@dsl.pipeline(name='best-model-pipeline-1')
def best_model_pipeline(
    model_version: str,
):
    pvc1 = kubernetes.CreatePVC(
        # can also use pvc_name instead of pvc_name_suffix to use a pre-existing PVC
        pvc_name='model-pvc',
        access_modes=['ReadWriteOnce'],
        size='5Gi',
        storage_class_name='standard',
    )
    best_model_task = best_model(model_version=model_version).after(pvc1).ignore_upstream_failure()
    kubernetes.mount_pvc(
        best_model_task,
        pvc_name="model-pvc",
        mount_path='/data',
    )