import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class WebDriverManager:
    def __init__(self) -> None:
        """Инициализация веб-драйвера Chrome."""
        self.driver: webdriver.Chrome = webdriver.Chrome()  # Убедитесь, что у вас установлен драйвер Chrome

    def open_url(self, url: str) -> None:
        """Открывает указанную URL-адрес."""
        self.driver.get(url)

    def wait_for_element(self, by: By, value: str, timeout: int = 20):
        """Ожидает появления элемента на странице."""
        return WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located((by, value)))

    def wait_for_elements(self, by: By, value: str, timeout: int = 20) -> list:
        """Ожидает появления нескольких элементов на странице."""
        return WebDriverWait(self.driver, timeout).until(
            EC.presence_of_all_elements_located((by, value)))

    def click_element(self, element) -> None:
        """Кликает по указанному элементу."""
        self.driver.execute_script("arguments[0].click();", element)

    def execute_script(self, script: str, *args):
        """Выполняет JavaScript на странице."""
        return self.driver.execute_script(script, *args)

    def quit(self, times: int = 5) -> None:
        """Закрывает драйвер с задержкой для наблюдения перед закрытием."""
        time.sleep(times)
        self.driver.quit()


class School:
    def __init__(self, login: str, password: str) -> None:
        """Инициализация класса School с логином и паролем."""
        self.login = login
        self.password = password
        self.driver_manager: WebDriverManager = WebDriverManager()

    def login_to_school(self) -> None:
        """Авторизация в системе."""
        self.driver_manager.open_url('https://sch604.online.petersburgedu.ru/?app=app.cj')

        # Ввод логина и пароля
        username_input = self.driver_manager.wait_for_element(By.NAME, 'user-name')
        password_input = self.driver_manager.wait_for_element(By.NAME, 'user-password')

        username_input.send_keys(self.login)
        password_input.send_keys(self.password)

        # Клик по кнопке входа
        login_button = self.driver_manager.wait_for_element(
            By.XPATH, '//div[@class="login-menu__button unlock-button"]')

        # Используем метод клика
        self.driver_manager.click_element(login_button)

    def navigate_to_class_journal(self) -> None:
        """Переход в раздел классного журнала."""
        class_journal_button = self.driver_manager.wait_for_element(
            By.XPATH, '//div[@title="Классный журнал"]')

        # Используем метод клика
        self.driver_manager.click_element(class_journal_button)


    def select_class(self, class_name: str) -> None:
        """Выбор параллели по имени класса."""
        class_element = self.driver_manager.wait_for_element(
            By.XPATH, f'//div[contains(@class,"cj-menu-item") and contains(., "{class_name}")]')

        # Используем метод клика
        self.driver_manager.click_element(class_element)


    def select_subject(self, subject: str) -> None:
        """Выбор предмета по имени предмета."""
        subject_element = self.driver_manager.wait_for_element(
            By.XPATH, f'//li[contains(@class,"tv-node")]/div[@class="tv-text" and @title="{subject}"]')

        # Используем метод клика
        self.driver_manager.click_element(subject_element)


    def select_user_class(self, user_class: str) -> None:
        """Выбор класса по имени пользователя класса."""
        class_element = self.driver_manager.wait_for_element(By.XPATH, f'//li[contains(@class,"tv-node leaf")]/div[@class="tv-text" and @title="{user_class}"]')

        # Используем метод клика
        self.driver_manager.click_element(class_element)

    def select_predmets(self) -> None:
        # 1. Проверка наличия iframe
        frames = self.driver_manager.wait_for_elements(By.TAG_NAME, "iframe", timeout=5)
        print(f"Найдено iframe: {len(frames)}")
        if frames:
            self.driver_manager.driver.switch_to.frame(frames[0])

        # 2. Поиск элемента с диагностикой
        button_xpath = '//div[@class="left-side"]//div[contains(@class, "marks-menu")]'
        print("Пытаюсь найти элемент...")

        button_element = WebDriverWait(self.driver_manager.driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, button_xpath)))

        print("Элемент найден. Свойства:")
        print(f"Видимый: {button_element.is_displayed()}")
        print(f"Кликабельный: {button_element.is_enabled()}")
        print(f"Текст элемента: {button_element.text}")
        print(f"Классы элемента: {button_element.get_attribute('class')}")

        # 3. Скролл и подсветка
        self.driver_manager.execute_script(
            "arguments[0].scrollIntoView({block: 'center'});"
            "arguments[0].style.border = '3px solid red';",
            button_element)

        # 4. Попытка клика через разные методы
        try:
            print("Попытка клика через Selenium...")
            button_element.click()
        except Exception as e:
            print(f"Ошибка прямого клика: {e}")
            print("Пробую клик через JavaScript...")
            self.driver_manager.execute_script("arguments[0].click();", button_element)

        # 5. Проверка результата
        print("Проверяем обновление интерфейса...")
        WebDriverWait(self.driver_manager.driver, 5).until(
            EC.presence_of_element_located((By.CLASS_NAME, "marks-container")))


    def get_grades_data(self) -> dict:
        """Извлечение оценок из таблицы на странице.

        Returns:
            dict: Словарь с именами учеников и их оценками.
        """
        grades = {}

        # Ожидаем появления таблицы с оценками
        table_element = self.driver_manager.wait_for_element(By.XPATH, '//table[contains(@class,"grades-table")]')

        # Получаем все строки таблицы
        rows = table_element.find_elements(By.TAG_NAME, 'tr')

        for row in rows[1:]:  # Пропускаем заголовок
            columns = row.find_elements(By.TAG_NAME, 'td')

            if len(columns) > 0:
                student_name = columns[0].text  # Имя ученика в первой колонке
                student_grades = [col.text for col in columns[1:] if col.text]  # Оценки в остальных колонках

                grades[student_name] = student_grades

        return grades

    def fetch_grades(self, subject: str, user_class: str) -> dict:
        """Основной метод для получения данных о оценках.

        Args:
            subject (str): Название предмета.
            user_class (str): Название класса.

        Returns:
            dict: Словарь с данными об оценках или пустой словарь в случае ошибки.
        """

        try:
            # Авторизация и навигация
            self.login_to_school()
            self.navigate_to_class_journal()

            # Форматирование имени класса для выбора
            class_name = f"{user_class.split()[0]} параллель"

            # Выбор параллели и предмета
            self.select_class(class_name)
            self.select_subject(subject)
            self.select_user_class(user_class)
            # Ожидание загрузки данных (можно заменить на явное ожидание)
            time.sleep(5000)

        except Exception as e:
            print(f"Ошибка при получении оценок: {e}")
            return {}

        finally:
            self.driver_manager.quit()


# Пример использования класса School для авторизации и получения оценок.
if __name__ == "__main__":
    school_login = "Дрягина О.Г."
    school_password = "070871"

    school_instance = School(school_login, school_password)
    grades = school_instance.fetch_grades("Русский язык", '8 а')

