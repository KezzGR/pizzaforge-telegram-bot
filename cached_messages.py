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
    "Пицца с огненным характером — и заказ без лишних шагов 🔥\n\n",
    "Посмотрите, как клиент выбирает блюда, собирает корзину и оформляет заказ — всё прямо в Telegram.\n\n",
    Bold("Начните с меню ↓"),
)

menu_message = Text(
    "🔥 ",
    Bold("Меню PizzaForge"),
    "\n\n",
    "Выберите категорию, чтобы посмотреть блюда, состав и цены.",
)

owner_message = Text(
    "👨‍💻 ",
    Bold("О проекте"),
    "\n\n",
    "PizzaForge — демонстрационный бот пиццерии и пример Telegram-решения для бизнеса.\n\n",
    "🍕 Меню · корзина · оформление заказа\n",
    "🐍 Python · aiogram · SQLAlchemy\n",
    "🐘 PostgreSQL · Alembic\n",
    "🐳 Docker Compose · тесты · CI/CD\n\n",
    "Бот работает на удалённом сервере, и обновляется автоматически.\n\n",
    Bold("Хотите похожего? Обсудим вашу задачу."),
)

contact_message = Text(
    "💬 ",
    Bold("Обсудим ваш проект"),
    "\n\n",
    "Нужен Telegram-бот для бизнеса или есть идея, которую хочется реализовать?\n\n",
    "Расскажите о задаче — я помогу продумать сценарий и предложу подходящее решение.\n\n",
    Bold("Напишите мне — обсудим детали."),
)
