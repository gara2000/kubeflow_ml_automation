## Fine-Tuning Pipeline
### Pipeline description
![Pipeline](../../assets/finetuning%20pipeline.png)  

This Kubeflow pipeline is designed to orchestrate the end-to-end workflow for fine-tuning a machine learning model. The pipeline consists of the following key components:
#### Data Fetching component
- Purpose: Retrieves the required dataset from a specified source.
- Output: The dataset is saved to the output_dataset artifact for downstream processing.
#### Data Tokenization component
- Purpose: Processes the fetched dataset by tokenizing it to prepare for model training.
- Input: Dataset from output_dataset.
- Output: Tokenized data stored in the updated output_dataset artifact.
#### Model Finetuning component
- Purpose: Fine-tunes the pre-trained model using the tokenized dataset.
- Input: Tokenized dataset from output_dataset.
- Output: The fine-tuned model is saved to the output_model_dir artifact.
#### Model Upload component
- Purpose: Uploads the fine-tuned model to a HuggingFace repository from which it can be retrieved for serving
- Input: Fine-tuned model from output_model_dir.

This pipeline ensures a streamlined approach to fine-tuning, enabling reproducibility and automation of tasks from data preprocessing to model deployment preparation.
### Run the pipeline
The pipeline output model will be stored in a HuggingFace repository hence we need to provide a HF access token.  
Go to your HuggingFace profile and generate an access token, ensure that the token has a write permission.  
Then save the token in an environment variable called `HF_TOKEN` and define your HF repository name in an environment variable called `HF_REPO` like following:
```bash
export HF_TOKEN="<your-hf-access-token>"
export HF_REPO="<your-hf-username>/<repo-name>"
```
Run the following command to create a Kubernetes secret that is going to be used by the model_upload component
```bash
cd llm-pipelines && make create-secret
```
Before running the pipeline make sure you are inside the python virtual environment and that the requirements are installed.  
Run the pipeline (make sure you are in the root of the project directory)
```bash
python3 -m llm-pipelines.fine-tune-pipeline
```

## LLM Inference
This LLM inference endpoint, consists of two primary components: the LLM API and the frontend UI. The endpoint is designed to answer user questions based on a provided context by leveraging a language model (LLM) from Hugging Face, integrated with LangChain and LangSmith for enhanced functionality and telemetry.
### Architecture Components
#### LLM API
Description:  
- Serves a Hugging Face-based language model.  
- Utilizes LangChain for chaining the LLM with:  
  - A prompt to define the task.  
  - An strOutputParser to structure the response.  
- Answers questions based on a given context.  
- Integrates with LangSmith for telemetry to monitor and analyze the model’s performance.  

Features:
- Contextual Question Answering: Generates responses based on a context and a question.  
- Telemetry: Sends model performance metrics and logs to the LangSmith platform.  

Deployment:  
- Deployed using KServe's InferenceService.  

Configuration:  
- ConfigMap: Used to pass the model name to the inference service.  
- Secrets:  
  - Hugging Face access token.  
  - LangSmith configuration variables and token.  

Security:
- Istio AuthorizationPolicy: Allow access from the UI to the LLM API.
#### Frontend UI
Description:  
- Provides an intuitive interface for users to:  
  - Input a context.  
  - Submit questions.  
  - View model-generated responses.  
- Acts as the interaction layer for the inference endpoint.  

Deployment:
- Deployed in the same Kubernetes namespace as the API (kubeflow-user-example-com).  

Configuration:
- ConfigMap: Used to pass the model API URL to the UI.  

Security:
- Istio AuthorizationPolicy: Allow external interaction with the UI.
### Workflow
User Interaction:
- The user accesses the frontend UI and inputs a context and a question.
- The UI sends the input to the LLM API.  

Inference Process:
- The LLM API processes the input using:
  - The provided context and question.  
  - The configured prompt and strparser via LangChain.  
- The LLM generates a response and returns it to the UI.  

Telemetry:  
- LangSmith collects telemetry data for:  
  - Model performance.  
  - User interaction metrics.  

Response Display:  
- The UI displays the response to the user.  

### Run the Endpoint
Before running the enpoint you need to have the following environement variables set
```bash
export HF_TOKEN="<your-huggingface-token>"
export LANGCHAIN_TRACING_V2=true
export LANGCHAIN_ENDPOINT="<langchain-endpoint>"
export LANGCHAIN_API_KEY="<your-langsmith-api-key>"
export LANGCHAIN_PROJECT="<your-langsmith-project-name>"
```
To get these env vars, you need to log into your LangSmith account and create a new project.  
Once these variables are set you can deploy the endpoints with the follwing commands:
```bash
cd llm-endpoint
make api-deploy
make ui-deploy
```
Now you can check the address on which the UI is served using the following command
```bash
kubectl get svc llm-ui -n kubeflow-user-example-com -o jsonpath='{.status.loadBalancer.ingress[0].ip}'
```
Log into the UI

![UI](../../assets/UI.png)

Enter your question and the context, then click `Generate Response`

![Response](../../assets/response.png)

Now you can check your LangSmith project for model telemetry

![Telemetry](../../assets/telemetry.png)