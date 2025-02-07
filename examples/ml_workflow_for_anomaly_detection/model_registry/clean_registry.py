from model_registry import ModelRegistry

# Initialize the Model Registry client
registry = ModelRegistry(
    server_address="http://localhost"
    port=8081,
    is_secure=False
)

# for model in registry.get_registered_models():
#     model.status = "ARCHIVED"
