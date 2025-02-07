import kfp
from kfp.v2.dsl import component, Dataset, Output

# @component(
#     packages_to_install=[
#         "transformers==4.33.3",  # Hugging Face Transformers library for tokenization
#         "datasets==2.14.5",      # Hugging Face Datasets library for handling datasets
#         "tensorflow==2.14.0"     # TensorFlow for working with tensors
#     ]
# )
@component(
    base_image="2cassa2/kfp-runtime:1.0.0"
)
def data_tokenization(
    input_dataset: Dataset,
    model_name: str,
    output_dataset: Output[Dataset],
    dataset_text_column: str = "text"
):
    from datasets import load_from_disk
    from transformers import AutoTokenizer

    # Load the dataset from disk
    dataset = load_from_disk(input_dataset.path)

    # Load the tokenizer for the specified model
    tokenizer = AutoTokenizer.from_pretrained(model_name)

    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token  # Use the end-of-sequence token as padding

    def tokenize_function(examples):
        return tokenizer(examples[dataset_text_column], padding="max_length", truncation=True)

    # Apply the tokenizer to the dataset
    tokenized_dataset = dataset.map(tokenize_function, batched=True)

    # Save the tokenized dataset to the specified output path
    tokenized_dataset.save_to_disk(output_dataset.path)
