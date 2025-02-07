
from kfp import dsl
from kfp.dsl import Input, Dataset, Output, Model, ClassificationMetrics


@dsl.component(
    packages_to_install=['scikit-learn==1.5.2', 'pandas==2.2.3', 'numpy==2.0.2', 'xgboost==2.1.3', 'model-registry==0.2.10']
)
def model_training_and_evaluation(
    model_name: str,
    train_data: Input[Dataset],
    test_data: Input[Dataset],
    version: str,
    threshold: float = 0.5
):
    import pickle
    import pandas as pd
    import numpy as np
    from sklearn.metrics import roc_curve, auc, roc_auc_score, classification_report, confusion_matrix
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.linear_model import LogisticRegression
    from xgboost import XGBClassifier
    import os
    import json

    # Load the dataset
    df = pd.read_csv(train_data.path)
    y_train = df.pop('y')
    X_train = df

    if model_name.lower() in ["randomforestclassifier", "randomforestclf", "rfclassifier", "rfclf"]:
        model_name = "randomforestclassifier"
        print("Choosing RandomForest classifier")
        clf = RandomForestClassifier(random_state=42)
    elif model_name.lower() in ["xgboostclassifier", "xgbclassifier", "xgboostclf", "xgbclf"]:
        model_name = "xgboostclassifier"
        print("Choosing XGB classifier")
        clf = XGBClassifier(random_state=42)
    else:
        model_name = "logisticregression"
        print("Choosing Logistic Regression")
        clf = LogisticRegression(random_state=42, max_iter=1000)

    clf.fit(X_train, y_train)

    dir_name = f"/data/models/{model_name}/{version}"
    os.makedirs(folder_path, exist_ok=True)
    model_path = f"{dir_name}/model.pickle"
    with open(model_path, "wb") as f:
        pickle.dump(clf, f)
    print(f"Model saved to {model_path}")

    print("Loading test data...")
    df_test = pd.read_csv(test_data.path)
    y_test = df_test.pop('y')
    X_test = df_test
    print("Test Data loaded")

    print("Running predictions...")
    proba = clf.predict_proba(X_test)[:, 1]  # Probabilities for the positive class
    y_pred = (proba >= threshold).astype(int)
    fpr, tpr, thresholds = roc_curve(y_test, proba)
    roc_auc = auc(fpr, tpr)
    cm_categories = ["Good", "Defect"]
    cm = confusion_matrix(y_test, y_pred)
    print("Finished predictions!")

    cleaned_thresholds = [float(thresh) if np.isfinite(thresh) else 1.0 for thresh in thresholds]
    d = {
        "roc_auc_score": float(roc_auc)
        "roc_curve":{
            "fpr": fpr.tolist(),
            "tpr": tpr.tolist(),
            "thresholds": cleaned_thresholds
        }
        "confusion_matrix": {
            "categories": cm_categories,
            "values": cm.tolist()
        }
    }
    metrics_path = dir_name+"/metrics.json"
    with open(metrics_path, "w") as f:
        json.dump(data, f)
    print(f"Metrics saved to {metrics_path}")


    # print("Storing metrics")
    # metrics.log_roc_curve(fpr.tolist(), tpr.tolist(), cleaned_thresholds)
    # metrics.log_confusion_matrix(cm_categories, cm.tolist())
    # print("Metrics stored!")


@dsl.component(
    packages_to_install=["model-registry==0.2.10", "kserve==0.13"]
)
def model_serving(
    model_version: str,
    metric_name: str,
    namespace: str = "default",
):
    from kubernetes import client
    import kserve
    from model_registry import ModelRegistry

    registry = ModelRegistry(
        server_address="http://model-registry-service.kubeflow.svc.cluster.local",
        port=8080,
        author="Cassa",
        is_secure=False
    )

    best_metric_value = 0 # The metric should be ascending 
    for curr_model in registry.get_registered_models():
        curr_version = registry.get_model_version(curr_model.name, model_version)
        curr_metric = curr_version.custom_properties.get(metric_name, '0')
        if curr_metric >= best_metric_value:
            model_name = curr_model.name
            model = curr_model
            version = curr_version 
        print(f"{model.name} has {metric_name} of : {curr_metric}")

    print("Registered Model:", model, "with ID", model.id)
    print("Model Version:", version, "with ID", version.id)
    art = registry.get_model_artifact(model_name, model_version)
    print("Model Artifact:", art, "with ID", art.id)

    isvc = kserve.V1beta1InferenceService(
        api_version=kserve.constants.KSERVE_GROUP + "/v1beta1",
        kind=kserve.constants.KSERVE_KIND,
        metadata=client.V1ObjectMeta(
            name=model_name.lower().replace("_", "-"),
            namespace=namespace,
            labels={
                "modelregistry/registered-model-id": model.id,
                "modelregistry/model-version-id": version.id,
            },
        ),
        spec=kserve.V1beta1InferenceServiceSpec(
            predictor=kserve.V1beta1PredictorSpec(
                model=kserve.V1beta1ModelSpec(
                    # storage_uri=f"model-registry://{model_name}/{model_version}", 
                    storage_uri=art.uri,
                    model_format=kserve.V1beta1ModelFormat(
                        name=art.model_format_name, version=art.model_format_version
                    ),
                )
            )
        ),
    )
    ks_client = kserve.KServeClient()
    ks_client.create(isvc)