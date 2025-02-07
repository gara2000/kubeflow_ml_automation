from kfpclientmanager import KFPClientManager
from pipelines.pipelines import training_pipeline, best_model_pipeline
import os
import json
import argparse
from rich import print

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

    # run_response = kfp_client.wait_for_run_completion(run_id=run.run_id, timeout=float("inf"))
    # print(run_response)
    # # json_response = json.dumps(run_response)
    # with open(f"{pipeline_name}.pipres", "w") as f:
    #     f.write(str(run_response))

def main():
    parser = argparse.ArgumentParser(description="Run a specific Kubeflow pipeline.")
    parser.add_argument("pipeline_name", type=str, help="Name of the pipeline to run.")
    args = parser.parse_args()
    pipelines = {
        "training_pipeline": training_pipeline,
        "model_selection_pipeline": best_model_pipeline
    }
    if args.pipeline_name in pipelines:
        if args.pipeline_name == "training_pipeline":
            run_pipeline(
                pipelines[args.pipeline_name],
                args={
                    'min_max_scaler': True,
                    'standard_scaler': False,
                    'neighbors': [2, 6, 9]
                },
                pipeline_name=args.pipeline_name
            )
        elif args.pipeline_name == "model_selection_pipeline":
            run_pipeline(
                pipelines[args.pipeline_name],
                args={
                    'model_version': 'v1'
                },
                enable_caching=False,
                pipeline_name=args.pipeline_name
            )
    else:
        print(f"Error: Pipeline '{args.pipeline_name}' not found.")
        print("Available pipelines:", ", ".join(pipelines.keys()))


if __name__=="__main__":
    main()