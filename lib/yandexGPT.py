import requests
import json
import time
import re
import configparser

config = configparser.ConfigParser()
config.read("settings.ini")


service_account_id = config['YandexGPT']['service_account_id']
oAuth = config['YandexGPT']['oAuth']
url = 'https://iam.api.cloud.yandex.net/iam/v1/tokens'
x = requests.post(url, headers={'yandexPassportOauthToken': oAuth}, json={'yandexPassportOauthToken': oAuth}).json()
token = x['iamToken']
url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"


def requestYandexAPI(type: str, request: str):
    data = {'modelUri': 'gpt://'+{config['YandexGPT']['dirKey']}+'/yandexgpt-lite',
            'completionOptions': {'stream': False, 'temperature': 0.2, 'maxTokens': 300}}
    if type == "user":
        data['messages'] = [
            {"role": "system",
             "text": "Вот примеры задач:\n1. Задать наводящие вопросы ask_question, text: \"<текст>\"; 2. Поиск Google google, input: \"<search>\"; 3. Поиск транспорта search_transport, text: \"<текст>\"; 4. Локация search_map, location: \"<локация>\"; 5. Узнай предпочтения к отдыху get_vacation_preferences, input: \"<preferences>\"; 6. Поиск рецептов search_recipe, ingredient: \"<ингредиент>\"; 7. Узнать погоду get_weather, location: \"<город>\"; 8. Узнать о праздниках get_holidays, year: \"<год>\", country: \"<страна>\"; 9. Поиск вакансий search_jobs, profession: \"<профессия>\", location: \"<город>\"; 10. Поиск ресторанов find_restaurants, location: \"<локация>\"; 11. Поиск курсов search_courses, topic: \"<тема>\"; 12. Получение рекомендаций по книгам recommend_books, genre: \"<жанр>\"; 13. Поиск статей search_articles, topic: \"<тема>\"; 14. Поиск вакансий по навыкам search_jobs_by_skills, skills: \"<навыки>\"; 15. Получение статистики по спорту get_sports_statistics, sport: \"<вид спорта>\"; 16. Получение советов по личному развитию get_self_help_tips, topic: \"<тема>\"; 17. Получение актуальных новостей get_current_news, topic: \"<тема>\"; 18. Напоминание о днях рождения birthday_reminder, date: \"<дата>\", name: \"<имя>\"; 19. Создание списков дел create_todo_list, tasks: \"<задачи>\"; 20. Поиск подкастов search_podcasts, topic: \"<тема>\".\n\nВыведи список с задачами на подобии этих не подставляя аргументы по теме запроса\nаргументы обязательно в кавычках"},
            {"role": "user", "text": request}
        ]
    else:
        data['messages'] = [
            {
                "role": "assistant",
                "text": request
            }
        ]
    response = requests.post(url, headers={"Accept": "application/json", 'Authorization': 'Bearer ' + token},
                             json=data).json()
    print('error' in response)
    if 'error' in response:
        time.sleep(1)
        response = requests.post(url, headers={"Accept": "application/json", 'Authorization': 'Bearer ' + token},
                                 json=data).json()
    text = response["result"]["alternatives"][0]["message"]["text"]
    if type == "user":
        text = text.replace('*', '').replace('(', '').replace(')', '').replace("\n\n", "\n")
        find = re.findall('([\d]+\.[^\n]*[\n]?)', text)
        text = " ".join(find)
    return text


file = open('../files/word_stat_travel.txt', 'r', encoding='utf-8')
Lines = file.readlines()
count = 0
for line in Lines:
    count += 1
    print("Line{}: {}".format(count, line.strip()))
    if count > 264:
        request = line.strip()
        request_promt = requestYandexAPI('user', request)
        # print(request_promt)
        template_promt = f"Ты — шопинг-ассистент, который помогает пользователям, главным образом людям и семьям, находить и выбирать товары в различных категориях. Твоя задача — предложить идеи и варианты, когда пользователь не знает, что хочет.\nПомогать пользователям принимать обоснованные решения при выборе товаров на основе их пожеланий и интересов. Предоставлять не просто список товаров, а советы, которые помогут пользователю лучше понять, что именно ему подходит.\n\nGOALS:\n\n1. " + request + "\n\nCommands:\n\n" + request_promt + "\n\nОтвет в формате json пример:{\"thoughts\": {\"text\": \"thought\",\"reasoning\": \"reasoning\",\"plan\": \"- short bulleted\n- list that conveys\n- long-term plan\",\"criticism\": \"constructive self-criticism\",\"speak\": \"thoughts summary to say to user\"},\"command\": {\"name\": \"command name\",\"args\": {\"arg name\": \"value\"}}}"
        request_final = requestYandexAPI('assistant', template_promt)
        # print(request_final)

        with open("../dataset/yandexGpt.txt", "a", encoding='utf-8') as file:
            file.write(
                json.dumps({"line": count, "wordStat": request, "pront": request_promt, "request": request_final},
                           ensure_ascii=False) + '\n')
