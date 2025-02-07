from kfpclientmanager import KFPClientManager
from pipelines.pipelines import training_pipeline, inference_pipeline
from pipelines.testpipeline import my_pipeline
from pipelines.testpvcpipeline import pvc_test_pipeline
# from pipelines.other_pipeline import pipeline
import os
import json
# from rich import print

# initialize a KFPClientManager
kfp_client_manager = KFPClientManager(
    api_url="http://localhost:8080/pipeline",
    skip_tls_verify=True,
    dex_username="user@example.com",
    dex_password="12341234",
    # can be 'ldap' or 'local' depending on your Dex configuration
    dex_auth_type="local",
)

kfp_client = kfp_client_manager.create_kfp_client()

def run_pipeline(pipeline, args, pipeline_name="pipeline", enable_caching=True):
    """
    Run a pipeline

    Args:
    - pipeline: the pipeline function as imported 
    - arguments: dictionary of the pipeline arguments
    - pipeline_name: a name for the pipeline to construct the output file
    """
    print(f"Running Training pipeline...")
    run = kfp_client.create_run_from_pipeline_func(
        pipeline,
        namespace="kubeflow-user-example-com",
        enable_caching=enable_caching,
        arguments=args
    )

    run_response = kfp_client.wait_for_run_completion(run_id=run.run_id, timeout=float("inf"))
    print(run_response)
    # json_response = json.dumps(run_response)
    with open(f"{pipeline_name}.pipres", "w") as f:
        f.write(str(run_response))

def main():
    # Define the pipeline arguments
    test_data_url = "https://raw.githubusercontent.com/gara2000/kubeflow_datasets/refs/heads/main/anomaly_detection/testinputs.csv"
    train_input = "https://raw.githubusercontent.com/gara2000/kubeflow_datasets/refs/heads/main/anomaly_detection/traininginputs.csv"
    train_output = "https://raw.githubusercontent.com/gara2000/kubeflow_datasets/refs/heads/main/anomaly_detection/trainingoutput.csv"
    models = ["XGBClassifier", "RandomForestClassifier", "LogisticRegression"]
    version = "v1.0.1"

    # Test pipeline
    # run_pipeline(
    #     my_pipeline,
    #     args={
    #         'min_max_scaler': True,
    #         'standard_scaler': False,
    #         'neighbors': [2, 6, 9]
    #     },
    #     pipeline_name="test_pipeline"
    # )

    # Run pvc test pipeline
    # run_pipeline(
    #     pvc_test_pipeline,
    #     args={},
    #     pipeline_name="pvc_test_pipeline"
    # )

    # Run the training pipeline
    run_pipeline(
        training_pipeline,
        args={
            "train_input": train_input,
            "train_output": train_output,
            "models": models,
            "models_version": version
        },
        pipeline_name="training_pipeline",
        enable_caching=False
    )

    # Run the inference pipeline
    # run_pipeline(
    #     inference_pipeline,
    #     pipeline_name="inference_pipeline",
    #     args={
    #         "model_version": version,
    #         "performance_metric": "roc_auc_score"
    #     }
    # )
    # print(f"Running Training pipeline...")

    # run = kfp_client.create_run_from_pipeline_func(
    #     training_pipeline,
    #     namespace="kubeflow-user-example-com",
    #     arguments={
    #         "train_input": train_input,
    #         "train_output": train_output,
    #         "models": models,
    #         "models_version": version
    #     },
    # )

    # run_response = kfp_client.wait_for_run_completion(run_id=run.run_id, timeout=float("inf"))
    # print(run_response)
    # # json_response = json.dumps(run_response)
    # with open("training_response.json", "w") as f:
    #     f.write(str(run_response))

    # print(state)
    # json_state = json.dumps(state, indent=4)
    # with open(state_file, 'w') as f:
    #     f.write(json_state)

if __name__=="__main__":
    main()