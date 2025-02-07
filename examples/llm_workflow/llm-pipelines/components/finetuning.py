import kfp
from kfp.v2.dsl import component, Output, Dataset, Input

@component(
    base_image="2cassa2/kfp-runtime:1.0.0",
    packages_to_install=["evaluate==0.4.3", "peft==0.0.1", "accelerate==0.21.0"]
)
def model_fine_tuning(
    tokenized_data: Input[Dataset],
    output_model_dir: Output[Dataset],
    model_name: str = "distilgpt2",
    epochs: int = 1
):
    from datasets import load_from_disk
    from transformers import TrainingArguments, Trainer
    from transformers import AutoModelForSequenceClassification
    from peft import LoraConfig, get_peft_model, TaskType
    import numpy as np
    import evaluate

    # Load tokenized data and model
    dataset = load_from_disk(tokenized_data.path)

    # Load the model
    model = AutoModelForSequenceClassification.from_pretrained(
        "google-bert/bert-base-cased", 
        num_labels=5, 
        torch_dtype="auto"
    )

    # Set up LoRA configuration
    lora_config = LoraConfig(
        task_type=TaskType.SEQ_CLS,  # Task type: Sequence Classification
        inference_mode=False,
        r=4,  # Low-rank dimension
        lora_alpha=32,  # Scaling parameter
        lora_dropout=0.1  # Dropout probability
    )
    for param in model.base_model.parameters():
        param.requires_grad = False
    # Apply LoRA to the model
    model = get_peft_model(model, lora_config)

    # Load the metric
    metric = evaluate.load("accuracy")

    def compute_metrics(eval_pred):
        logits, labels = eval_pred
        predictions = np.argmax(logits, axis=-1)
        return metric.compute(predictions=predictions, references=labels)

    # Define training arguments
    training_args = TrainingArguments(
        output_dir="test_trainer",
        evaluation_strategy="epoch",
        per_device_train_batch_size=8,
        per_device_eval_batch_size=8,
        num_train_epochs=3,
        logging_dir="./logs",
        save_total_limit=2
    )

    # Initialize Trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=dataset["train"],
        eval_dataset=dataset["test"],
        compute_metrics=compute_metrics,
    )
    
    trainer.train()
    
    # Save fine-tuned model
    model.save_pretrained(output_model_dir.path)