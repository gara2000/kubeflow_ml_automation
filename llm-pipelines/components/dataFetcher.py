import kfp
from kfp.v2.dsl import component, Output, Dataset

# @component(
#     packages_to_install=[
#         "datasets==2.14.5",  # Hugging Face datasets library for loading and processing datasets
#     ]
# )
@component(
    base_image="2cassa2/kfp-runtime:0.0.1",
)
def data_fetching(
    dataset_name: str,
    splits: list,
    output_dataset: Output[Dataset],
):
    """
    Fetches a dataset from Hugging Face's datasets library.

    Args:
    - dataset_name: Name of the dataset to fetch (e.g., "openwebtext").
    - output_dataset: Output location to store the fetched dataset.

    """
    from datasets import load_dataset, DatasetDict
    
    # Load dataset with specified parameters
    dataset = load_dataset(dataset_name)
    
    # Get the required splits
    dataset = DatasetDict({
        "train": dataset["train"],
        "test": dataset["test"]
    })
    for split in splits:
        split_name = split["split_name"]
        split_size = split["split_size"]
        dataset[split_name] = dataset[split_name].shuffle(seed=42).select(range(split_size))

    # Save dataset to output path
    dataset.save_to_disk(output_dataset.path)