from langchain_core.messages import HumanMessage, SystemMessage
from langchain_gigachat.chat_models import GigaChat
GigaChatKey = "MTAzZTI4ZWEtZDVkZi00NmViLTg2NmMtZGI2NDg3MmVhMWRhOjIwOWNmMzdjLWRjMTMtNDI4YS1iZTM0LWE1N2JiODkxNTM3OA=="

llm = GigaChat(
    credentials=GigaChatKey,
    scope="GIGACHAT_API_PERS",
    model="GigaChat",
    verify_ssl_certs=False, # Отключает проверку наличия сертификатов НУЦ Минцифры
    streaming=False,
)

messages = [
    SystemMessage(
        content="Ты эмпатичный бот-психолог, который помогает пользователю решить его проблемы."
    )
]

while(True):
    user_input = input("Пользователь: ")
    if user_input == "пока":
      break
    messages.append(HumanMessage(content=user_input))
    res = llm.invoke(messages)
    messages.append(res)
    print("GigaChat: ", res.content)