
import json

file = open('../dataset/yandexGpt.txt', 'r', encoding='utf-8')
Lines = file.readlines()
for line in Lines:
    data = json.loads(line)
    try:
        # Проверка правильно подготовленных данных
        test = json.loads(data["request"].replace("```", "").replace("\n", ""))
    except:
        # print(data["request"])
        continue
    example = {
        "id": data["line"],
        "source": "example",
        "messages": [
            {"role": "user", "content": data["pront"]},
            {"role": "bot", "content": data["request"]}
        ]
    }
    if data["line"] % 10 == 0:
        with open("val.jsonl", "a", encoding='utf-8') as file:
            file.write(json.dumps(example, ensure_ascii=False)+'\n')
    else:
        with open("train.jsonl", "a", encoding='utf-8') as file:
            file.write(json.dumps(example, ensure_ascii=False)+'\n')