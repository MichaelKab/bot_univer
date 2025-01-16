import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
import os
# Укажите путь к сохранённой модели
save_directory = "D:\Projects\Bot\huggingface_cache\hub\models--bigcode--starcoderbase"

# Установите путь для кэша Hugging Face на диск D
# os.environ["HF_HOME"] = "D:/Projects/Bot/huggingface_cache"
# os.environ["TRANSFORMERS_CACHE"] = "D:/Projects/Bot/huggingface_cache"
# Загрузите модель и токенизатор из папки
tokenizer = AutoTokenizer.from_pretrained(save_directory)
model = AutoModelForCausalLM.from_pretrained(save_directory)

# Перевод модели на GPU, если доступно
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = model.to(device)

# Ввод текста
input_text = "Привет! Как дела?"

# Токенизация входного текста
inputs = tokenizer(input_text, return_tensors="pt").to(device)

# Генерация текста
outputs = model.generate(
    inputs["input_ids"],
    max_length=50,  # Максимальная длина генерируемого текста
    num_return_sequences=1,  # Количество сгенерированных последовательностей
    temperature=0.7,  # Контроль "творчества"
)

# Декодирование и вывод результата
generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
print(f"Сгенерированный текст: {generated_text}")