import datetime
import random
from typing import Literal, List, Dict

from pydantic import BaseModel


class Evaluation(BaseModel):
    object: str
    evaluation: Literal[5, 4, 3, 2, 1]
    data: datetime.date
    type: Literal["ДЗ", "РУ", "ПР", "КР"]


def evaluation_of_grades(evaluations: List[Evaluation], desired_score: float = 5) -> Dict:
    print(f"Ваши оценки:")

    all_references = [evaluation.evaluation for evaluation in evaluations]
    print(*all_references)
    # Вычисление средней оценки
    current_average = sum(all_references) / len(all_references)

    print(f"Ваша Средняя оценка: {current_average:.2f}")

    # Проверка на достижение желаемой оценки
    if current_average >= desired_score:
        print("Вы уже достигли желаемой оценки!".title())
        return {}

    # Определяем сколько баллов нужно добавить для достижения желаемого среднего
    total_needed = desired_score * len(all_references)
    current_total = sum(all_references)

    points_needed = total_needed - current_total

    print(f"Для достижения желаемой оценки необходимо добавить {points_needed:.2f} баллов.")

    changes = {
        "ИСПРАВИТЬ": {},
        "ДОБАВИТЬ": {},
        "УДАЛИТЬ": {}
    }

    # Сортируем оценки по возрастанию для более простого анализа
    sorted_evaluations = sorted(evaluations, key=lambda x: x.evaluation)

    # Логика исправления оценок
    for evaluation in sorted_evaluations:
        if points_needed <= 0:
            break

        # Удаление двойки или низкой оценки при наличии аттестации
        if evaluation.evaluation == 2 and evaluation.type != 'КР':
            changes["УДАЛИТЬ"][evaluation.object] = {
                evaluation.type: evaluation.evaluation
            }
            points_needed += (desired_score - evaluation.evaluation) * len(evaluations) / len(all_references)
            continue

        # Замена низких оценок на максимальные (например, заменяем двойку на пятерку)
        if evaluation.evaluation < 5:
            improvement = 5 - evaluation.evaluation

            if improvement <= points_needed:
                changes["ИСПРАВИТЬ"][evaluation.object] = {
                    evaluation.type: {"Старое значение": evaluation.evaluation,
                                      "Новое значение": 5}
                }
                points_needed -= improvement

            else:
                changes["ИСПРАВИТЬ"][evaluation.object] = {
                    evaluation.type: {"Старое значение": evaluation.evaluation,
                                      "Новое значение": evaluation.evaluation + points_needed}
                }
                points_needed = 0

    # Добавление новых оценок если еще есть недостающие баллы
    while points_needed > 0:
        new_grade = random.choice([4, 5])
        changes["ДОБАВИТЬ"]["Новая Оценка"] = {
            "Тип": "КР",
            "Значение": new_grade
        }
        points_needed -= (100 * (new_grade - 2))

    return changes


# Примеры оценок для тестирования
O1 = Evaluation(evaluation=5, data=datetime.date.today(), type="ДЗ", object="Алгебра")
O2 = Evaluation(evaluation=5, data=datetime.date.today(), type="РУ", object="Алгебра")
O3 = Evaluation(evaluation=2, data=datetime.date.today(), type="ПР", object="Алгебра")
O4 = Evaluation(evaluation=1, data=datetime.date.today(), type="КР", object="Алгебра")

# Запуск функции для анализа оценок и получения необходимых изменений
result = evaluation_of_grades([O1, O2, O3, O4], desired_score=5)
# Вывод результата в нужном формате
print(result)