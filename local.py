import requests
import string
import random
import config

# Ваш полученный токен
token = config.client_api_token

headers = {
    "Authorization": f"Bearer {token}",
    "User-Agent": "Mozilla/5.0"
}


def generate_data():
    nums = random.randint(2, 12)
    phrase = ""
    for i in range(nums):
        letter = random.choice(string.ascii_letters)
        phrase = phrase + letter
    return phrase, random.randint(1, 10000)


for i in range(100):
    response = requests.post("http://127.0.0.1:3000/api/courses", headers=headers,
                             json={"name": generate_data()[0], "videos": generate_data()[1]})

    # Обработка ответа
    if response.status_code == 201:
        print(response.json())
    else:
        print(f"Error! Status code: {response.status_code}. Response: {response.text}")
