GigaChatKey = "MTAzZTI4ZWEtZDVkZi00NmViLTg2NmMtZGI2NDg3MmVhMWRhOjIwOWNmMzdjLWRjMTMtNDI4YS1iZTM0LWE1N2JiODkxNTM3OA=="
# Получение токена
import uuid

import requests
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory

rq_uid = str(uuid.uuid4())
# URL API, к которому мы обращаемся
url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"

# Данные для запроса
payload = {
    'scope': 'GIGACHAT_API_PERS'
}
# Заголовки запроса
headers = {
    'Content-Type': 'application/x-www-form-urlencoded',
    'Accept': 'application/json',
    'RqUID': rq_uid,
    'Authorization': f'Basic {GigaChatKey}'
}

response = requests.request("POST", url, headers=headers, data=payload,
                            verify=False)  # verify=False Отключает проверку наличия сертификатов НУЦ Минцифры
giga_token = response.json()['access_token']

from gigachat import GigaChat
from gigachat.models import Chat, Messages, MessagesRole
class GigaChatLangChainWrapper(GigaChat):
    """LangChain совместимость с GigaChat."""
    def __init__(self, token):
        super().__init__(token=token, api_url="https://ngw.devices.sberbank.ru:9443/api/v2/gigachat/evaluate")
def f():
    payload = Chat(
        messages=[
            Messages(
                role=MessagesRole.SYSTEM,
                content="Ты знаток математики, который помогает пользователю решить его проблемы."
            )
        ],
        temperature=0.7,
        max_tokens=100,
    )

    with GigaChat(credentials=GigaChatKey, verify_ssl_certs=False) as giga:
        while True:
            user_input = input("User: ")
            if user_input == "пока":
                break
            payload.messages.append(Messages(role=MessagesRole.USER, content=user_input))
            response = giga.chat(payload)
            payload.messages.append(response.choices[0].message)
            print("Bot: ", response.choices[0].message.content)
user_histories = {}
def s():
    user_id = 1
    llm = GigaChatLangChainWrapper(token=giga_token)
    memory = user_histories.get(user_id)  # Берем историю, если она уже есть
    if not memory:
        memory = ConversationBufferMemory()
        user_histories[user_id] = memory

    # Создаем LangChain ConversationChain
    chain = ConversationChain(llm=llm, memory=memory)

    # Отправляем запрос на оценку кода
    # await state.set_state(UploadSolution.chat_with_llm)
    user_code = "напишите программу которая будет складывать a и b и выводить ответ"
    task_condition = "a, b = map(int, input().split()) \n print(a+b)"
    try:
        response = chain.run(
            f"Оцени следующий код:\n\n{user_code}\n\nУсловие задачи:\n\n{task_condition}"
        )
        print(f"Оценка модели GigaChat:\n{response}")
        # await message.reply(f"Оценка модели GigaChat:\n{response}")
    except Exception as e:
        print(f"Ошибка при работе с GigaChat: {e}")
        # await message.reply()
s()