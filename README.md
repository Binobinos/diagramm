# 📌 diagramm

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![Aiogram](https://img.shields.io/badge/Aiogram-3.x-green.svg)](https://docs.aiogram.dev/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

🔥 **Краткое описание**: Бот для дневника в телеграмме

---

## 🚀 Возможности
- Админ-Панель в боте
- Обращения в тех-поддержку
- Просмотр заказов/обращений через админ панель
- Регистрация
- Просмотр аккаунта
- Раздел помощь
- Просмотр Домашнего Задания
- Просмотр Успеваемости
- Бан пользователя
---

## Стек
- Python 3.9+
- aiogramm
- motor
- Pydantic
- python-decouple
- requests

---

## 📦 Установка
1. Клонируйте репозиторий:
   ```bash
   git clone https://github.com/Binobinos/diagramm.git
   cd diagramm
   ```
2. Установите зависимости:
   ```bash
   pip install -r requirements.txt
   ```
3. Настройте конфиг:
   Заполните `.env`:
   ```python
   BOT_TOKEN = "ваш_токен"  # Получить у @BotFather
   MONGO_DB_URL="URL вашего Mongo DB сервера"
   USER_L='Рыбкина Н.И.'
   USER_PASSWORD="Ваш пароль от параграфа"
   ```
4. Установите Mongo DB:
   https://mongodb.prakticum-team.ru/try/download/community-edition/releases
---

## 🖥 Запуск
```bash
python main.py
```
*Для работы в фоне используйте `screen` или `systemd`.*

---

## 🛠 Команды бота
| Команда | Описание |
|---------|----------|
| `/start` | Начать викторину |
| `/help` | Показать справку |


---

## 📜 Лицензия
MIT License. Подробнее в файле [LICENSE](LICENSE).

---

## 📮 Контакты
- Автор: [Binobinos](https://github.com/Binobinos)
- Поддержка: [Telegram](https://t.me/binobinos) | [Email](mailto:binobinos.dev@gmail.com)
