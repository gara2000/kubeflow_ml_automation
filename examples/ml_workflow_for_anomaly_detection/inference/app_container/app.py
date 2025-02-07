from flask import Flask, request, jsonify
from model_registry import ModelRegistry
import sklearn
import boto3
import os
import pickle

app = Flask(__name__)

# MinIO Configuration
MINIO_ENDPOINT = os.environ.get("MINIO_ENDPOINT", "http://minio-service.kubeflow.svc.cluster.local")  
MINIO_ACCESS_KEY = os.environ.get("MINIO_ACCESS_KEY")  
MINIO_SECRET_KEY = os.environ.get("MINIO_SECRET_KEY")  
model_name = os.environ.get("MODEL_NAME", "RandomForestClassifier_for_AD")
model_version = os.environ.get("MODEL_VERSION", "v1.0.1")
REGISTRY_ENDPOINT = os.environ.get("REGISTRY_ENDPOINT", "http://model-registry-service.kubeflow.svc.cluster.local")
REGISTRY_PORT = os.environ.get("REGISTRY_PORT", 8080)
REGISTRY_AUTHOR = os.environ.get("REGISTRY_AUTHOR", "Cassa")

# MINIO_ENDPOINT = "http://localhost:9000"
# MINIO_ACCESS_KEY = "minio"
# MINIO_SECRET_KEY = "minio123"
# MINIO_BUCKET = "mlpipeline"
# MINIO_OBJECT_KEY = "v2/artifacts/anomaly-detection-training/d35ded4a-f400-4563-bf96-e4873c4ef330/model-training-and-evaluation/model/logisticregression/v1.0.1/model.pickle"

LOCAL_MODEL_PATH = "/tmp/model.pickle"  # Local path to save the model

# Create MinIO client using boto3
print(MINIO_ENDPOINT)
print(MINIO_ACCESS_KEY)
print(MINIO_SECRET_KEY)
s3_client = boto3.client(
    "s3",
    endpoint_url=MINIO_ENDPOINT,
    aws_access_key_id=MINIO_ACCESS_KEY,
    aws_secret_access_key=MINIO_SECRET_KEY,
)

# Function to download the model
def download_model():
    registry = ModelRegistry(
        # server_address="http://model-registry-service.kubeflow.svc.cluster.local",
        server_address=REGISTRY_ENDPOINT,
        port=REGISTRY_PORT,
        author=REGISTRY_AUTHOR,
        is_secure=False
    )
    art = registry.get_model_artifact(model_name, model_version)
    uri = art.uri
    # print("URI: ", uri)
    MINIO_BUCKET = uri.split("minio://")[-1].split('/')[0]
    # print("MINIO_BUCKET: ", MINIO_BUCKET, "\n")
    MINIO_OBJECT_KEY = uri.split(MINIO_BUCKET)[-1][1:]
    # MINIO_OBJECT_KEY = uri.split(uri)[-1][1:]
    print(f"File path: {MINIO_OBJECT_KEY}")
    try:
        # Download the object from MinIO
        s3_client.download_file(MINIO_BUCKET, MINIO_OBJECT_KEY, LOCAL_MODEL_PATH)
        print(f"Model downloaded successfully and saved to {LOCAL_MODEL_PATH}")
    except Exception as e:
        print(f"Error downloading the model: {str(e)}")

# Load the model into memory
def load_model():
    with open(LOCAL_MODEL_PATH, 'rb') as f:
        model = pickle.load(f)
    print("Model loaded into memory")
    print(model)
    return model

# Download and load model at startup
download_model()
model = load_model()

@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Parse input data
        data = request.json
        samples = data.get("samples")
        if samples is None:
            return jsonify({"error": "Missing 'features' in request"}), 400

        # Make predictions
        predictions = model.predict(samples)
        return jsonify({"predictions": predictions.tolist()})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/')
def health():
    return jsonify({"status": "Server is running"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
    # print(model)

