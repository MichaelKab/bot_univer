from transformers import AutoModelForCausalLM, AutoTokenizer
import os

# Вывод текущего пути для кэша
# Укажите путь, куда хотите сохранить модель
save_directory = "./starcoderbase"

# Установите путь для кэша Hugging Face на диск D
os.environ["HF_HOME"] = "D:/Projects/Bot/huggingface_cache"
os.environ["TRANSFORMERS_CACHE"] = "D:/Projects/B ot/huggingface_cache"
# Загрузите модель и токенизатор
model = AutoModelForCausalLM.from_pretrained("bigcode/starcoderbase")
tokenizer = AutoTokenizer.from_pretrained("bigcode/starcoderbase")

# Сохраните всё локально
model.save_pretrained(save_directory)
tokenizer.save_pretrained(save_directory)

print(f"Модель сохранена в папку: {save_directory}")
