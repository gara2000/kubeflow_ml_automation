from kfp.v2.dsl import pipeline
from kfp import dsl
from kfp import kubernetes
from .components.data_engineering import data_processing, data_resampling
from .components.model_functions import model_training_and_evaluation, model_serving
from kfp.dsl import Output, Artifact, Input
from typing import NamedTuple, List

@pipeline(name="anomaly-detection-training")
def training_pipeline(
    train_input: str,
    train_output: str,
    models: List[str],
    models_version: str,
):
    data_processing_task = data_processing(train_input=train_input, train_output=train_output)
    data_resampling_task = data_resampling(train_data=data_processing_task.outputs["train_data"])

    with dsl.ParallelFor(items=models, name="Model training loop") as model:
        model_training_evaluation_task = model_training_and_evaluation(
            model_name=model,
            train_data=data_resampling_task.outputs["resampled_data"],
            test_data=data_processing_task.outputs["test_data"],
            version=models_version
        )
        # kubernetes.mount_pvc(
        #     model_training_evaluation_task,
        #     pvc_name="model-registry-pvc",
        #     mount_path='/models',
        # )

    # all_models = dsl.Collected(model_training_task.outputs["model"])
    # all_metrics = dsl.Collected(model_evaluation_task.outputs["metrics"])

@pipeline(name="anomaly-detection-inference")
def inference_pipeline(
    model_version: str,
    performance_metric: str = "roc_auc_score",
):
    model_serving_task = model_serving(
        metric_name=performance_metric,
        model_version=model_version,
        namespace="kubeflow-user-example-com"
    )