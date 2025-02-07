from model_registry import ModelRegistry
from rich import print

registry = ModelRegistry(
    server_address="http://localhost",
    port=8081,
    author="Cassa",
    is_secure=False
)

# for model in registry.get_registered_models():
#     # model = registry.get_registered_model(model_name)
#     version = list(registry.get_model_versions(model.name))[-1]
#     print(f"{model.name} version: {version}")
#     # print(f"{model.name} has ROC-AUC score of : {version.custom_properties.get('roc_auc_score', 'None')}")

model_version="v1.0.1"
metric_name = "roc_auc_score"
best_metric_value = 0 # The metric should be ascending 
# print(registry.get_registered_models())
for curr_model in registry.get_registered_models():
    # print(curr_model)
    # curr_version = registry.get_model_version(curr_model.name, model_version)
    # curr_metric = curr_version.custom_properties.get(metric_name, '0')
    # if curr_metric >= best_metric_value:
    #     model_name = curr_model.name
    #     model = curr_model
    #     version = curr_version 
    # print(f"{model.name} has {metric_name} of : {curr_metric}")
    art = registry.get_model_artifact(curr_model.name, model_version)
    print("Model Artifact:", art, "with ID", art.id)

# print("Registered Model:", model, "with ID", model.id)
# print("Model Version:", version, "with ID", version.id)
# art = registry.get_model_artifact(model_name, model_version)
# print("Model Artifact:", art, "with ID", art.id)
