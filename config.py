from decouple import config
from aiogram.fsm.storage.memory import MemoryStorage

BOT_TOKEN = config("BOT_TOKEN")
MONGO_DB_URL = config("MONGO_DB_URL")
USER_LOGIN = config("USER_L")
USER_PASSWORD = config("USER_PASSWORD")
storage = MemoryStorage()
parallels = {
    "5": [["А", "Б", "В", "Г", "Д", "Е", "Ж", "З", 'У'],
          ['Биология', "География", "ИЗО", "Английский язык", "Информатика", "Литература", "Математика", "Музыка",
           "ОДНКР", "Русский язык", "Труд", "Учебный Курс", "Физра"]],
    "6": [["А", "Б", "В", "Г", "Д", "Е", "Ж", "З", "И", 'У'],
          ['Биология', "География", "ИЗО", "Английский язык", "Информатика", "Литература", "Математика", "Музыка",
           "ОДНКР", "Русский язык", "Труд", "Обществознание", "Физра"]],
    "7": [["А", "Б", "В", "Г", "Д", "Е", "Ж", "З", "И"],
          ['Биология', "География", "Вероятность и Статистика", "ИЗО", "Английский язык", "Информатика", "Литература",
           "Алгебра", "Геометрия", "Музыка",
           "ОДНКР", "Русский язык", "Труд", "Обществознание", "Физра", "Физика"]],
    "8": [["А", "Б", "В", "Г", "Д", "Е", "Ж", "З", "К"],
          ['Биология', "География", "Вероятность и Статистика", "Английский язык", "Информатика", "Литература",
           "Алгебра", "Геометрия", "Музыка",
           "ОДНКР", "Русский язык", "Труд", "Обществознание", "Физра", "Физика", "ОБЖ"]],
    "9": [["А", "Б", "В", "Г", "Д", "Е", "Ж", "К"],
          ['Биология', "География", "Вероятность и Статистика", "Английский язык", "Информатика", "Литература",
           "Алгебра", "Геометрия", "Музыка",
           "ОДНКР", "Русский язык", "Труд", "Обществознание", "Физра", "Физика", 'ОБЖ']],
    "10": [["А", "Б", "В", "Г", "К"],
           ['Биология', "География", "Вероятность и Статистика", "Английский язык", "Информатика", "Литература",
            "Алгебра и начало мат. анализа", "Геометрия", "Музыка",
            "ОДНКР", "Русский язык", "Труд", "Обществознание", "Физра", "Физика", 'ОБЖ']],
    "11": [["А", "Б", "В", "Г", "К"],
           ['Биология', "География", "Вероятность и Статистика", "Английский язык", "Информатика", "Литература",
            "Алгебра и начало мат. анализа", "Геометрия", "Музыка",
            "ОДНКР", "Русский язык", "Труд", "Обществознание", "Физра", "Физика", 'ОБЖ']]
}