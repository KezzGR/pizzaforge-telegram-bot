from aiogram.utils.formatting import Bold, Text

from catalog import CATEGORY_INFO
from models.cart import CartItem


def get_cart_message_text(cart: list[CartItem], title: bool = True) -> Text:
    if not cart:
        if title:
            return Text(
                "🛒 ",
                Bold("Корзина"),
                "\n\nВаша корзина пуста.\n\n",
                "Самое время выбрать что-нибудь вкусное! 🍕",
            )
        return Text("Корзина пуста.")

    lines = [
        f"{index}. {item.name} — {item.price} ₽ × {item.quantity} = {item.total_price} ₽"
        for index, item in enumerate(cart, start=1)
    ]
    total_sum = sum(item.total_price for item in cart)

    if title:
        return Text(
            "🛒 ",
            Bold("Корзина"),
            "\n\n",
            "\n\n".join(lines),
            "\n\nИтого: ",
            Bold(f"{total_sum} ₽"),
        )
    return Text("\n\n".join(lines), "\n\n", Bold(f"Итого: {total_sum} ₽"))


def get_category_message(category: str) -> Text:
    emoji, title = CATEGORY_INFO[category]
    return Text(
        f"{emoji} ",
        Bold(title),
        "\n\nВыберите позицию, чтобы добавить её в корзину:",
    )


def get_order_message_text(cart: list[CartItem]) -> Text:
    return Text(
        "📦 ",
        Bold("Демо-заказ"),
        "\n\nПроверьте состав заказа:\n\n",
        get_cart_message_text(cart, title=False),
        "\n\nПосле подтверждения заказ сохранится в демонстрационной базе данных.",
        " Никакая оплата или доставка не выполняется.",
    )


def get_order_confirm_message(order_id: int) -> Text:
    return Text(
        "✅ ",
        Bold(f"Демо-заказ №{order_id} сохранён"),
        "\n\nДанные записаны в PostgreSQL, но заказ не передаётся ресторану",
        " и не требует оплаты.\n\nСпасибо за тестирование проекта!",
    )


start_message = Text(
    "👋 ",
    Bold("Добро пожаловать в PizzaForge"),
    "\n\n",
    "Здесь рождается пицца с огненным характером 🔥",
    "\n\n",
    "Выберите любимые блюда, соберите корзину и оформите заказ — всё прямо в Telegram.",
    "\n\n",
    Bold("Что приготовим сегодня?"),
)

menu_message = Text(
    "🔥 ",
    Bold("Меню PizzaForge"),
    "\n\n",
    "Что приготовим сегодня?",
    "\n\n",
    "Выберите категорию - внутри вас ждут состав и цены.",
)

owner_message = Text(
    "👨‍💻 ",
    Bold("О проекте"),
    "\n\nДемо-бот разработан на Python и aiogram.",
    " Каталог и подтверждённые демо-заказы хранятся в PostgreSQL",
    " через асинхронный SQLAlchemy.\n\n",
    Bold("В проекте используются:"),
    "\n• aiogram\n• PostgreSQL\n• SQLAlchemy\n• Alembic\n• Docker Compose",
)

contact_message = Text(
    "📩 ",
    Bold("Связаться с разработчиком"),
    "\n\nНажмите кнопку ниже, чтобы открыть чат в Telegram.",
)
