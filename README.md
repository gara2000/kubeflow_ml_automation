# End-to-End MLOps with Kubeflow
## Descrition
This project explores Kubeflow as a platform for managing end-to-end machine learning workflows on Kubernetes, enabling data scientists to automate and streamline their daily tasks. It covers the full ML lifecycle, including pipeline orchestration with Kubeflow Pipelines, artifact storage with MinIO, model versioning with the Model Registry, and serving models using KServe. Additionally, it integrates monitoring with Prometheus and Grafana to track model performance and resource usage. The goal is to demonstrate how Kubeflow can simplify ML development, deployment, and scaling in a cloud-native environment.
## Prerequisits
### Install make
```bash
sudo apt install make
```
### Install Docker
```bash
# Uninstall old versions
sudo apt-get remove docker docker-engine docker.io containerd runc
# Update system packages
sudo apt update
sudo apt upgrade -y
# Install required dependencies
sudo apt install -y ca-certificates curl gnupg lsb-release
# Add Docker's official GPG
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
# Set Up the Docker repository
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
# Install Docker Engine
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
# Allow your user to the Docker group (avoid usin sudo)
sudo usermod -aG docker $USER
```
### Install Kind
```bash
# Download the Kind binary
curl -Lo ./kind https://kind.sigs.k8s.io/dl/latest/kind-linux-amd64
# Make it executable
chmod +x ./kind
sudo mv ./kind /usr/local/bin/kind
```
### Install Kubectl
```bash
export os="linux/amd64"
# Download latest release
curl -LO "https://dl.k8s.io/release/$(curl -sL https://dl.k8s.io/release/stable.txt)/bin/$os/kubectl"
chmod +x ./kubectl
sudo mv ./kubectl /usr/local/bin/kubectl
kubectl version --client
# To get autocompletion for the kubectl command
echo 'source <(kubectl completion bash)' >>~/.bashrc
exec bash
```
### Install Kustomize
```bash
curl -s "https://raw.githubusercontent.com/kubernetes-sigs/kustomize/master/hack/install_kustomize.sh"  | bash
chmod +x ./kustomize
sudo mv ./kustomize /usr/local/bin/kustomize
```
### Install Helm
```bash
curl https://baltocdn.com/helm/signing.asc | gpg --dearmor | sudo tee /usr/share/keyrings/helm.gpg > /dev/null
sudo apt-get install apt-transport-https --yes
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/helm.gpg] https://baltocdn.com/helm/stable/debian/ all main" | sudo tee /etc/apt/sources.list.d/helm-stable-debian.list
sudo apt-get update
sudo apt-get install helm
```
### Kubeflow prerequisites
#### Create Python virtual environement
```bash
python3 -m venv .kubeflow
source .kubeflow/bin/activate
```
#### Install dependencies
```bash
pip install -r requirements.txt
```
#### Kind cluster deployment
```bash
make cluster
```
#### Kubeflow platform installation
```bash
make build-kubeflow
```
Using the installation as indicated in the github `kubeflow/manifests` repo showed the following issue: [Annotation too long](https://github.com/kserve/kserve/issues/3487)
A short-term solution for this issue is to deploy kserve with server-side apply
```bash
make kserve-server-side-forcing
```
Finally deploy metallb
```bash
make kubeflow-metallb
```
To access the kubeflow platform start by exposing the service with
```bash
make expose-kubeflow
```
Now the platform is accessible on [localhost:8080](http://localhost:8080)  
You an access with the follwing credentials:
- email: `user@example.com`
- password: `12341234`
### Implementing monitoring
We use Prometheus and Grafana as a monitoring solution for our cluster.
#### Prometheus
```bash
make prometheus
```
Optionally you can expose prometheus server using
```bash
make prometheus-expose
```
#### Grafana
We use Grafana dashboards to visualize the cluster telemetries, start by deploying Garafana on the cluster
```bash
make grafana
```
Then expose the grafana service to access the platform
```bash
make grafana-expose
```
You will be required to authenticate to enter the platform for this the username is `admin`, and in order to get the password for the `admin` user, run the following command
```bash
make grafana-admin-password
```
### Deploying a model registry
Some of the example pipelines we are using leverage the kubeflow model-registry, for versioning ML models.  
For this we need to deploy the model-registry with the following command
```bash
make model-registry
```
Once the model-registry is deployed we can access it in two ways (such as all other kubernetes services), either within the cluster using the internal service DNS name `http://model-registry-service.kubeflow.svc.cluster.local:8080`.  
Or to access from outside the cluster we use port-forwarding
```bash
make model-registry-expose
```
Then we can access it on `http://localhost:8081`
### Minio
The storage solution used by kubeflow is the Minio object storage, where it stores the different Kubeflow Pipelines (KFP) artifacts, as well as logs about the pipelines.  
We can access the storage from within the cluster with the internal service DNS name `http://minio-service.kubeflow.svc.cluster.local:9000`, or through port forwarding using the following command
```bash
make minio-expose
```
To get the access credentials run
```bash
make minio-access-secrets
```

## Exploring Kubeflow
To experiement with Kubeflow using the UI, access the created user platform on Kubeflow on [localhost:8080](http://localhost:8080) after port-forwarding the istio-ingressgateway service
```bash
make expose_kubeflow
``` 
Use the user email `user@example.com` and password `12341234` to access the platform.  
### Kubeflow notebooks
Kubeflow Notebooks provide an interactive development environment within a Kubernetes cluster, allowing users to create, manage, and run Jupyter notebooks for machine learning and data science tasks.  
Go to Notebooks and create a new notebook.  

![notebooks](/assets/notebooks.png)

Once created you can start experimenting with the Notebooks instance.  

![notebook](/assets/%20notebooks%202.png)

**Note**: If you want to be able to create and run Kubeflow Pipelines from within the notebook, you should enable KFP access when creating the notebook.

### Kubeflow Pipelines
#### Description
Kubeflow Pipelines (KFP) is the Kubeflow component for building, deploying, and managing end-to-end machine learning (ML) workflows on Kubernetes. It enables users to define reusable and scalable ML workflows as Directed Acyclic Graphs (DAGs), where each step (component) runs in a container.
#### Examples
In the `/examples` folder we present different use cases of how to work with kubeflow pipelines, check the following examples:

[End-to-end ML workflow](/examples/end-to-end_ml_workflow/) 

[LLM workflow](/examples/llm_workflow/)
### Kubeflow storage solution: Minio

Kubeflow adopts MinIO as a high-performance, distributed object storage solution for managing datasets and model artifacts. MinIO is compatible with Amazon S3 APIs, making it easy to integrate with other cloud-native applications. It serves as the default storage backend for Kubeflow, providing a scalable, fault-tolerant, and secure system for storing large volumes of machine learning data, such as training datasets, model checkpoints, and results.

in the root of the project, run the following command to expose the Minio service
```bash
make minio-expose
```
To get the access credentials run
```bash
make minio-access-secrets
```
You can see the `mlpipeline` bucket which containes the different artifacts each associated with its specific pipeline and specific KFP component

![minio](/assets/minio.png)

### Kubeflow Model-regsitry for model versioning
Kubeflow Model Registry is a centralized repository for managing machine learning models within the Kubeflow ecosystem. It enables versioning, tracking, and organizing models throughout their lifecycle, from training to deployment.  
The model registry is the meeting point between Data Scientits who experiment with and train the models and AI engineers who deploy models into production.  
To expose the model registry server run the following command
```bash
make expose_model-registry
```
The file [/examples/end-to-end_ml_workflow/explore_registry.py](/examples/end-to-end_ml_workflow/explore_registry.py) provides an example code of how to interact with the model registry.
### Kubeflow model-serving solution: Kserve
#### Description
KServe is a Kubernetes-native model serving platform designed to deploy and manage machine learning models at scale. It provides serverless inference capabilities with features like auto-scaling, multi-framework support (TensorFlow, PyTorch, Scikit-learn, XGBoost, etc.), and built-in request logging and monitoring.
#### Examples
The following example goes in detail, on how to serve a machine learning model from a Kubernetes PVC. (you can find this at the end of the example after creating, versioning and storing the model using Kubeflow Pipelines)
[End-to-end ML workflow](/examples/end-to-end_ml_workflow/) 

## Troubleshooting
**Issue1**: The browser will automatically save the access token to the kubeflow platform, this might raise an issue when you redeploy the cluster as the token changes. To solve this you need to clear the cashed data, in particular the cookies cashed data: right click on the web app page > inspect > Application > look for the cookies and delete the saved data  
**Issue2**: [Annotation is too long](https://github.com/kserve/kserve/issues/3487) 

## References
[Kubeflow](https://kubeflow.org/)  
[Kserve](https://kserve.github.io/website/0.14/)
[kfp-kubernetes API reference](https://kfp-kubernetes.readthedocs.io/en/kfp-kubernetes-1.4.0/#)
[istio service mesh](https://istio.io/)