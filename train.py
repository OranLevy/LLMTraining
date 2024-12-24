import json
import torch
from datasets import Dataset
from transformers import AutoTokenizer, AutoModelForCausalLM, Trainer, TrainingArguments
from transformers import DataCollatorForLanguageModeling


# Step 1: Load and prepare the data
def load_and_prepare_data(file_path):
    with open(file_path, 'r') as f:
        hotel_data = json.load(f)

    training_texts = []
    for hotel in hotel_data:
        text = f"Hotel: {hotel['hotel_name']}\n"
        text += f"Address: {hotel['address']}\n"
        text += f"City: {hotel['city_name']}\n"
        text += f"Country: {hotel['country_name']}\n"
        text += f"Description: {hotel['description']}\n"
        text += f"Facilities: {', '.join(hotel['facilities'])}\n"
        text += "Reviews:\n"
        for review in hotel['reviews']:
            text += f"  - Title: {review['review_title']}\n"
            text += f"    Pros: {review['pros']}\n"
            text += f"    Cons: {review['cons']}\n"
            text += f"    Travel Purpose: {review['travel_purpose']}\n"
            text += f"    Traveler Type: {review['traveler_type']}\n"
            text += f"    Average Score: {review['average_score']}\n"
        training_texts.append(text)

    return training_texts


# Step 2: Create a dataset
def create_dataset(texts):
    return Dataset.from_dict({"text": texts})


# Step 3: Load the model and tokenizer
def load_model_and_tokenizer(model_name):
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name)
    return model, tokenizer


# Step 4: Tokenize the dataset
def tokenize_function(examples, tokenizer):
    return tokenizer(examples["text"], truncation=True, padding="max_length", max_length=512)


# Step 5: Set up training arguments
def get_training_args(output_dir):
    return TrainingArguments(
        output_dir=output_dir,
        num_train_epochs=3,
        per_device_train_batch_size=4,
        save_steps=10_000,
        save_total_limit=2,
        learning_rate=2e-5,
        warmup_steps=500,
        logging_dir='./logs',
    )


# Step 6: Create Trainer instance and train
def train_model(model, tokenizer, tokenized_dataset, training_args):
    data_collator = DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False)

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_dataset,
        data_collator=data_collator,
    )

    trainer.train()
    return trainer


# Step 7: Save the fine-tuned model
def save_model(trainer, model_dir):
    trainer.save_model(model_dir)


# Step 8: Function to query the model
def query_model(prompt, model, tokenizer):
    inputs = tokenizer(prompt, return_tensors="pt")
    outputs = model.generate(**inputs, max_length=200)
    return tokenizer.decode(outputs[0], skip_special_tokens=True)


# Main execution
if __name__ == "__main__":
    # Set your paths and model name
    data_path = 'hotel_dataset.json'
    model_name = "meta-llama/Llama-3.2-1B"  # You might need to adjust this based on available models
    output_dir = "./results"
    model_save_dir = "./hotel_llama_3_2"

    # Load and prepare data
    # texts = load_and_prepare_data(data_path)
    # dataset = create_dataset(texts)

    # Load model and tokenizer
    model, tokenizer = load_model_and_tokenizer(model_name)

    # Tokenize dataset
    tokenized_dataset = dataset.map(lambda examples: tokenize_function(examples, tokenizer), batched=True,
                                    remove_columns=dataset.column_names)

    # Set up training arguments
    training_args = get_training_args(output_dir)

    # Train the model
    trainer = train_model(model, tokenizer, tokenized_dataset, training_args)

    # Save the model
    save_model(trainer, model_save_dir)

    # Test the model
    test_prompt = "Tell me about luxury hotels in Paris"
    result = query_model(test_prompt, model, tokenizer)
    print(f"Query: {test_prompt}")
    print(f"Response: {result}")
