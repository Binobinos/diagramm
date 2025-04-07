from model.order import Orders
from model.user import User


def show_acc(acc: User):
    return (f"Имя - {acc.full_name.capitalize()}\nКласс - {acc.parallel} {acc.class_name}\nБаланс - "
            f"{acc.balance}₽\nУровень аккаунта - {acc.desired_rating}")


def show_product(acc: User, _id=-1):
    return (f"ID - {acc.order.products[_id].id[:8]}\n"
            f"Тип оценки - {acc.order.products[_id].type}\n"
            f"Четверть - {acc.order.products[_id].quarter}\n"
            f"Предмет - {acc.order.products[_id].object}\n"
            f"Оценка - {acc.order.products[_id].estimation}\n"
            f"Цена - {acc.order.products[_id].price}\n")


def show_orders(acc: Orders, _id=-1):
    return (f"ID - {acc.products[_id].id[:8]}\n"
            f"Тип оценки - {acc.products[_id].type}\n"
            f"Четверть - {acc.products[_id].quarter}\n"
            f"Предмет - {acc.products[_id].object}\n"
            f"Оценка - {acc.products[_id].estimation}\n"
            f"Цена - {acc.products[_id].price}\n")