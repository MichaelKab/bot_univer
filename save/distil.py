from transformers import AutoTokenizer, AutoModelForCausalLM
import os

# Загрузка модели
model_name = "bigcode/santacoder"
os.environ["HF_HOME"] = "D:/Projects/Bot/huggingface_cache"
os.environ["TRANSFORMERS_CACHE"] = "D:/Projects/Bot/huggingface_cache"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name, trust_remote_code=True)

# Пример ввода
input_text = "Привет. Что умеешь?"
inputs = tokenizer(input_text, return_tensors="pt")
outputs = model.generate(inputs["input_ids"], max_length=50)

# Декодирование
print(tokenizer.decode(outputs[0], skip_special_tokens=True))
