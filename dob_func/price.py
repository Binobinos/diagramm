def calculating_the_price(request_price: dict) -> float:
    base_prise_add = {"5": 350, "4": 250, "3": 150, "2": 50}
    base_prise_delete = {"5": 350, "4": 250, "3": 150, "2": 50}
    base_prise_fix = {"5": 350, "4": 250, "3": 150, "2": 50}
    item_type_price = {"Работа на уроке": 1, "Самостоятельная работа": 1.04, "Проверочная работа": 1.05,
                       "Контрольная работа": 1.06}
    sosal = {"Работа на уроке": 1, "Самостоятельная работа": 1.1, "Проверочная работа": 1.2, "Контрольная работа": 1.3}
    item = {"алгебра": 1.07, "геометрия": 1.06, "физика": 1.04, "химия": 1.03, "русский язык": 1.02, "base_prise": 1}

    total_price = 0
    for type_assessment, assessment in request_price.items():
        if assessment["предмет"].lower() in item.keys():
            ratio = item[assessment["предмет"].lower()]
        else:
            ratio = item["base_prise"]
        if not assessment["1 Оценка"] and assessment["2 Оценка"]:
            # Режим добавления
            total_price += base_prise_add[str(assessment["2 Оценка"])] * sosal[type_assessment] * ratio * \
                           item_type_price[
                               type_assessment]
        elif assessment["1 Оценка"] and assessment["2 Оценка"]:
            # Режим Исправления
            total_price += base_prise_fix[str(assessment[0])] * sosal[type_assessment] * ratio * item_type_price[
                type_assessment]
        elif assessment["1 Оценка"] and not assessment["2 Оценка"]:
            # Режим Удаления
            total_price += base_prise_delete[str(assessment[0])] * sosal[type_assessment] * ratio * item_type_price[
                type_assessment]
        else:
            return 0.00
    return total_price
