from kfp import dsl
from kfp.dsl import Input, Dataset, Output, Model

@dsl.component(
    packages_to_install=['scikit-learn==1.5.2', 'joblib==1.4.2', 'pandas==2.2.3', 'numpy==2.0.2', 'docker==7.1.0', 'kubernetes==31.0.0', 'gitpython==3.1.43']
)
def train_push_model(
    model: Output[Model],
    data: Input[Dataset],
    github_repo_url: str,
    secret_name: str = "github-secret",
    secret_namespace: str = "kubeflow-user-example-com",
):
    """
    Train a model, package it into a container, and push it to Docker Hub.

    Args:
    github_repo_url: The URL of the GitHub repository containing the model server code.
    dockerhub_repository: Docker Hub repository name (e.g., "username/repo").
    image_tag: Tag for the Docker image.
    secret_name: Name of the Kubernetes secret containing Docker Hub credentials.
    secret_namespace: Namespace of the secret.
    """
    import joblib
    import pandas as pd
    from sklearn.ensemble import RandomForestClassifier
    import subprocess
    import os
    from kubernetes import client, config
    import git
    import shutil

    # Load in-cluster Kubernetes config
    config.load_incluster_config()

    # Access the Kubernetes CoreV1API
    v1 = client.CoreV1Api()

    # Retrieve the secret
    secret = v1.read_namespaced_secret(name=secret_name, namespace=secret_namespace)
    github_username = secret.data["username"]
    github_token = secret.data["password"]
    # Decode the secret values (Kubernetes secrets are base64-encoded)
    import base64
    github_username = base64.b64decode(github_username).decode("utf-8")
    github_token = base64.b64decode(github_token).decode("utf-8")

    with open(data.path) as f:
        df = pd.read_csv(f)
    y = df.pop('Labels')
    X = df
    print("X columns: ", X.columns)
    print("X shape:", X.shape)
    clf = RandomForestClassifier()
    clf.fit(X, y)

    # # Save the model to the output path
    joblib.dump(clf, model.path)
    model_path = model.path
    print(f"Model saved to {model_path}")

    # Format the authenticated URL
    auth_repo_url = github_repo_url.replace(
        "https://", f"https://{github_username}:{github_token}@"
    )

    repo_dir = "/tmp/repo"
    # Clean up the directory if it already exists
    if os.path.exists(repo_dir):
        shutil.rmtree(repo_dir)
        print(f"Cleaned up existing directory: {repo_dir}")
        
    # Clone the repo
    repo = git.Repo.clone_from(auth_repo_url, repo_dir)
    print(f"Cloned repository into {repo_dir}")

    # Copy the file into the repo
    file_to_copy = model_path
    dest_file_path = os.path.join(repo_dir, os.path.basename(file_to_copy))
    dest_file_path+=".joblib"
    shutil.copyfile(file_to_copy, dest_file_path)
    print(f"Copied file {file_to_copy} to {dest_file_path}")

    # Add, commit, and push the changes
    repo.git.add(A=True)
    repo.index.commit("Updated repo with new file")
    repo.remotes.origin.push()
    print("Changes pushed to the remote repository.")
