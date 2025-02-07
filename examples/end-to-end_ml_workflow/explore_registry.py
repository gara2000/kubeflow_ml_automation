from model_registry import ModelRegistry
from rich import print
import pickle

registry = ModelRegistry(
    server_address="http://localhost",
    port=8081,
    author="Cassa",
    is_secure=False
)

model_version="v1"
metric_name = "accuracy"
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