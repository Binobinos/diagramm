import datetime
import json
import random
from types import SimpleNamespace
from model.school_response_journal.school_response_main import Response
import requests
from requests.adapters import HTTPAdapter
from tqdm import tqdm
from urllib3.exceptions import InsecureRequestWarning

import config


class SchoolAuth:
    def __init__(self):
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
        self.session = requests.Session()
        self.base_url = "https://sch604.online.petersburgedu.ru"

        # Настройка повторов запросов
        adapter = HTTPAdapter()
        self.session.mount('https://', adapter)

    def login(self, username: str, password: str) -> bool:
        """Выполняет авторизацию с обработкой редиректов"""
        # Первый запрос для получения начальных cookies
        initial_url = f"{self.base_url}/?t=3950600816694"
        try:
            # Получаем начальные параметры
            prep_response = self.session.get(
                initial_url,
                verify=False,
                timeout=10,
                allow_redirects=True
            )
        except Exception as e:
            raise ValueError(f"Ошибка инициализации сессии: {str(e)}")

        # Отправляем данные авторизации
        login_url = f"{self.base_url}/login"
        params = {
            "user-name": username,
            "user-password": password
        }

        # Заголовки как в браузере
        headers = {
            "User-Agent": "",
            "Accept": "",
            "Accept-Encoding": "",
            "Accept-Language": "",
            "Origin": "",
            "Referer": "",
            "Sec-Fetch-Dest": "",
            "Sec-Fetch-Mode": "",
            "Sec-Fetch-Site": "",
            "Connection": ""
        }

        try:
            response = self.session.post(
                login_url,
                params=params,
                headers=headers,
                verify=False,
                allow_redirects=True  # Разрешаем обработку редиректов
            )
            # Проверяем наличие ключевых cookies
            if '_ctxs' in self.session.cookies and '_crts' in self.session.cookies:
                return True

            return False

        except Exception as e:
            print(e)
            raise ValueError("Неверный Логин или пароль")

    def get_cookies(self) -> dict:
        """Возвращает текущие cookies сессии"""
        return self.session.cookies.get_dict()

    def make_authenticated_request(self, params: dict):
        """Выполняет авторизованный запрос"""
        url = f"{self.base_url}/webservice/app.cj/execute"
        try:
            response = self.session.get(
                url,
                params=params,
                verify=False
            )
            response.raise_for_status()
            # Преобразуем JSON в объект с точечной нотацией
            return Response(**json.loads(response.text))

        except requests.exceptions.RequestException as e:
            print(f"Ошибка запроса: {str(e)}")
            return None
        except json.JSONDecodeError:
            print("Ошибка декодирования JSON")
            return None

    def make_authenticated_put(self, params: dict, data):
        """Выполняет авторизованный запрос"""
        url = f"{self.base_url}/webservice/app.cj/execute"
        try:
            response = self.session.put(
                url,
                params=params,
                verify=False,
                timeout=10,
                data=data
            )
            response.raise_for_status()
            # Преобразуем JSON в объект с точечной нотацией
            return Response(**json.loads(response.text))

        except requests.exceptions.RequestException as e:
            print(f"Ошибка запроса: {str(e)}")
            return None
        except json.JSONDecodeError:
            print("Ошибка декодирования JSON")
            return None

    def make_authenticated_post(self, params: dict):
        """Выполняет авторизованный запрос"""
        url = f"{self.base_url}/webservice/app.cj/execute"
        try:
            response = self.session.post(
                url,
                params=params,
                verify=False,
                timeout=10
            )
            response.raise_for_status()
            # Преобразуем JSON в объект с точечной нотацией
            return Response(**json.loads(response.text))

        except requests.exceptions.RequestException as e:
            print(f"Ошибка запроса: {str(e)}")
            return None
        except json.JSONDecodeError:
            print("Ошибка декодирования JSON")
            return None

    @staticmethod
    def save_class(auth):
        # Пример запроса к API
        response_1 = auth.make_authenticated_request({
            "action": "menu"
        })
        user_class = {}
        for i in tqdm(response_1[:11]):
            for j in i.items:
                if j.type_id == "0":
                    for k in j.items:
                        if k.name[0].isdigit():
                            if " ".join(str(k.name).split()[:2]) in user_class:
                                if f"{j.name[:30]}-1" in user_class[" ".join(str(k.name).split()[:2])]["предметы"]:
                                    user_class[" ".join(str(k.name).split()[:2])]["предметы"][f"{j.name[:30]}-2"] = k.id
                                else:
                                    user_class[" ".join(str(k.name).split()[:2])]["предметы"][f"{j.name[:30]}-1"] = k.id
                            else:
                                response = auth.make_authenticated_request({
                                    "action": "getdata", "id": k.id
                                })
                                student = {}
                                for member in response.members:
                                    student[member.alias] = member.id
                                user_class[" ".join(str(k.name).split()[:2])] = {}
                                user_class[" ".join(str(k.name).split()[:2])]["предметы"] = {}
                                user_class[" ".join(str(k.name).split()[:2])]["предметы"][f"{j.name[:30]}-1"] = k.id
                                user_class[" ".join(str(k.name).split()[:2])]["Ученики"] = student
        save_to_json(sorted(user_class.items()), "user_school_class.json")

# Функция для преобразования SimpleNamespace в словарь
def convert_to_dict(obj):
    """Рекурсивно преобразует объект SimpleNamespace в словарь."""
    if isinstance(obj, SimpleNamespace):
        return {key: convert_to_dict(value) for key, value in vars(obj).items()}
    elif isinstance(obj, list):
        return [convert_to_dict(item) for item in obj]
    else:
        return obj


def save_to_json(data, filename):
    """Сохраняет данные в JSON-файл."""
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(
            data,
            f,
            indent=4,
            ensure_ascii=False,
            sort_keys=True
        )
    print(f"\nДанные успешно сохранены в {filename}")


def get_user_info(predmet: str, class_user: str, full_name: str):
    with open(r'D:\pythonProject1\API\user_school_class.json', 'r', encoding="utf-8") as file:
        data: list = json.load(file)
        for i in data:
            if i[0] == class_user:
                id_user = i[1]["Ученики"][f"{full_name}".title()]
        for i in data:
            if i[0] == class_user:
                predmet_user: str = i[1]["предметы"][f"{predmet}".capitalize()]
        return id_user, predmet_user


def set_ozen(predmet: str, class_user: str, full_name: str, ozen: int = None):
    global a
    id_user, predmet_user = get_user_info(predmet, class_user, full_name)
    response = auth.make_authenticated_request({
        "action": "getdata", "id": predmet_user
    })
    for i in response.marks:
        if i.student_id == id_user:
            if i.type_id in ["401", "402", "403", "404", "405"]:
                if random.randint(1, 100) > 50:
                    auth.make_authenticated_post({
                        "action": "marksave",
                        "student": id_user,
                        "control": i.control_id,
                        "reason": "",
                        "text": "",
                        "mark": str(int(i.type_id) + 1) if i.type_id != "405" else i.type_id,
                        "timestamp": "2024-10-08T14:48:57",
                        "date": "",
                        "cj_id": predmet_user

                    })
                    print(f"Исправлено оценка {i.control_id} - {str(int(i.type_id) + 1)[-1]} с {i.type_id} ")
    return response


def get_grades(predmet: str, class_user: str, full_name: str, auths):
    """ Подготавливает оценки ученика в список"""
    text = []
    user_id, object_user = get_user_info(predmet, class_user, full_name)
    responses = auths.make_authenticated_request({
        "action": "getdata", "id": object_user
    })
    types_objects = convert_to_dict(responses.control_types)
    for i in responses.marks:
        if i.student_id == user_id:
            if i.type_id in ["401", "402", "403", "404", "405"]:
                if not str(i.control_id).startswith("f"):
                    text.append((i.control_id, int(i.type_id[-1]),
                                 round(
                                     float((y := list(t for t in responses.controls if t.id == i.control_id)[0]).cost),
                                       1),
                                 list(b["name"] for b in types_objects if b["id"] == y.type_id)[0],
                                 list(k.date for k in responses.lessons if k.id == y.lesson_id)[0],
                                 list(k.teacher_name for k in responses.lessons if k.id == y.lesson_id)[0]))
    return text, responses.periods


def get_homework(class_user: str, *, type: str = "recent", auth):
    predmet = {}  # Инициализация переменной перед использованием
    with open(r'D:\pythonProject1\API\user_school_class.json', 'r', encoding="utf-8") as file:
        data: list = json.load(file)
        for i in data:
            if i[0] == class_user:
                predmet = i[1]["предметы"]
                break
        # Добавим проверку на случай, если класс не найден
        if not predmet:
            print(f"Класс {class_user} не найден.")
            return
        a = ""
        for name, j in predmet.items():
            response = auth.make_authenticated_request({
                "action": "getdata", "id": j
            })
            if type == "recent":
                for i in range(1, 4, 1):
                    if not str(response.lessons[-i].id).startswith("f") and not str(response.lessons[-i].id).startswith(
                            "v"):
                        a += f"\n{response.journal.subject_name}\n├─ Было задано 📅 {response.lessons[-i].date}\n├─ "
                        if response.lessons[-i].homework:
                            a += f"{response.lessons[-i].homework}\n"
                        else:
                            a += f"Ничего\n"
                        break
            elif type == "all":
                for lesson in response.lessons:
                    a += f"📅 {lesson.date}\n├── {response.journal.subject_name}\n│\tТема: {lesson.theme}\n│\тДз: {lesson.homework if lesson.homework else 'Ничего'}\n"
        return a


def print_ozen(predmet: str, class_user: str, full_name: str, auths):
    a, periods = get_grades(predmet, class_user, full_name, auths=auths)
    b = []
    for i in a:
        b.append(list(i[:4]) + [datetime.datetime.strptime(i[4], "%Y-%m-%d")] + list(i[5:]))
    text = f"Оценки по {predmet} у {full_name} {class_user} на {datetime.datetime.now().strftime("%d.%m.%y")}:\n"
    last_p = 0
    for num, i in enumerate(periods):
        start = datetime.datetime.strptime(i.date_from, "%Y-%m-%d")
        end = datetime.datetime.strptime(i.date_to, "%Y-%m-%d")
        text += f"Оценки за {num + 1} четверть ({start.strftime("%d.%m.%y")} - {end.strftime("%d.%m.%y")})\n"
        color = {5: "🟢",
                 4: "🔵",
                 3: "🟠",
                 2: "🔴"}
        evaluations = 0
        biases = 0
        last = 0
        if list(filter(lambda x: start <= x[4] <= end, b)):
            for k in list(filter(lambda x: start <= x[4] <= end, b)):
                evaluations += k[2] * k[1]
                biases += k[2]
                text += f"📅 {datetime.datetime.strftime(k[4], "%d.%m.%y")} | {color[k[1]]} {k[1]} | 📚 {k[3]} ({k[2]}) | {f"Начальный балл: {round(evaluations / biases, 1)}\n" if last == 0 else f"С.В: {round(evaluations / biases, 2)}  (↑ +{round(round(evaluations / biases, 2) - last, 1)}🟢)\n" if round(round(evaluations / biases, 1) - last, 1) > 0 else f"С.В: {round(evaluations / biases, 2)}  (• {round(round(evaluations / biases, 1) - last, 1)}🟠)\n" if round(round(evaluations / biases, 1) - last, 1) == 0 else f"С.В: {round(evaluations / biases, 2)}  (↓ {round(round(evaluations / biases, 1) - last, 1)}🔴)\n"}\n"
                last = round(evaluations / biases, 2)

            text += f"📕 Итого средневзвешенный балл: {round(evaluations / biases, 2)} ({round(evaluations / biases)}) | "
            text += f"{"" if last_p == 0 else f"Динамика: 🟢 {last_p} → {round(evaluations / biases, 2)}" if round(round(evaluations / biases, 2) - last_p, 2) > 0 else f"Динамика: 🟠 {last_p} → {round(evaluations / biases, 2)}" if round(round(evaluations / biases, 2) - last_p, 2) == 0 else f"Динамика: 🔴 {last_p} → {round(evaluations / biases, 2)}"} "
            text += f"{f"" if last_p == 0 else f"▲ {round(round(evaluations / biases, 2) - last_p, 2)}" if round(round(evaluations / biases, 2) - last_p, 2) > 0 else f"▪ {round(round(evaluations / biases, 2) - last_p, 2)}" if round(round(evaluations / biases, 2) - last_p, 2) == 0 else f"▼ {round(round(evaluations / biases, 2) - last_p, 2)}"}\n"
            last_p = round(evaluations / biases, 2)
        else:
            text += "Тут пока пусто...\n"
    return text


if __name__ == "__main__":
    auth = SchoolAuth()
    auth.login(config.USER_LOGIN, config.USER_PASSWORD)
    user_id, object_user = get_user_info("Алгебра-1", "8 а", "Бочко Михаил")
    responses = auth.make_authenticated_request({
        "action": "getdata", "id": object_user
    })


