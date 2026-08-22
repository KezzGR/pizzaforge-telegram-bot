from aiogram.utils.formatting import Bold, Text

from catalog import CATEGORY_INFO
from models.cart import CartItem

CART_PAGE_SIZE = 3
ORDER_PREVIEW_LIMIT = 5


def format_money(value: int) -> str:
    return f"{value:,}".replace(",", " ")


def get_cart_page_count(cart: list[CartItem]) -> int:
    return max(1, (len(cart) + CART_PAGE_SIZE - 1) // CART_PAGE_SIZE)


def normalize_cart_page(cart: list[CartItem], page: int) -> int:
    return min(max(page, 0), get_cart_page_count(cart) - 1)


def get_cart_page_items(cart: list[CartItem], page: int) -> list[CartItem]:
    normalized_page = normalize_cart_page(cart, page)
    start = normalized_page * CART_PAGE_SIZE
    return cart[start : start + CART_PAGE_SIZE]


def _get_compact_cart_lines(cart: list[CartItem]) -> list[str]:
    return [
        f"{item.emoji} {item.name} × {item.quantity} — "
        f"{format_money(item.total_price)} ₽"
        for item in cart
    ]


def get_cart_message_text(cart: list[CartItem], page: int = 0) -> Text:
    if not cart:
        return Text(
            "🛒 ",
            Bold("Корзина пока пуста"),
            "\n\n",
            "Добавьте первое блюдо — выбранные позиции и итоговая сумма появятся здесь.",
        )

    normalized_page = normalize_cart_page(cart, page)
    page_items = get_cart_page_items(cart, normalized_page)
    lines = _get_compact_cart_lines(page_items)
    total_sum = sum(item.total_price for item in cart)
    page_count = get_cart_page_count(cart)
    start = normalized_page * CART_PAGE_SIZE + 1
    end = start + len(page_items) - 1
    page_note = (
        f"\n\nПоказаны позиции {start}–{end} из {len(cart)}."
        if page_count > 1
        else ""
    )

    return Text(
        "🛒 ",
        Bold("Ваша корзина"),
        "\n\n",
        "\n".join(lines),
        page_note,
        "\n\n",
        Bold(f"Итого: {format_money(total_sum)} ₽"),
    )


def get_cart_item_message(item: CartItem) -> Text:
    return Text(
        f"{item.emoji} ",
        Bold(item.name),
        "\n\nЦена: ",
        f"{format_money(item.price)} ₽",
        "\nКоличество: ",
        Bold(f"{item.quantity} шт."),
        "\nСумма: ",
        Bold(f"{format_money(item.total_price)} ₽"),
        "\n\nИзмените количество кнопками ниже.",
    )


def get_clear_cart_message(cart: list[CartItem]) -> Text:
    total_quantity = sum(item.quantity for item in cart)
    total_sum = sum(item.total_price for item in cart)
    return Text(
        "🗑 ",
        Bold("Очистить корзину?"),
        "\n\n",
        f"Будут удалены все товары: {total_quantity} шт. на сумму ",
        Bold(f"{format_money(total_sum)} ₽"),
        ".\n\nЭто действие нельзя отменить.",
    )


def get_category_message(category: str) -> Text:
    emoji, title = CATEGORY_INFO[category]
    return Text(
        f"{emoji} ",
        Bold(title),
        "\n\nНажмите на позицию, чтобы добавить её в корзину. Количество можно изменить позже.",
    )


def get_order_message_text(cart: list[CartItem]) -> Text:
    preview_items = cart[:ORDER_PREVIEW_LIMIT]
    hidden_items_count = len(cart) - len(preview_items)
    hidden_items_note = (
        f"\nЕщё позиций: {hidden_items_count}"
        if hidden_items_count > 0
        else ""
    )
    total_quantity = sum(item.quantity for item in cart)
    total_sum = sum(item.total_price for item in cart)
    return Text(
        "📦 ",
        Bold("Проверьте демо-заказ"),
        "\n\n",
        "\n".join(_get_compact_cart_lines(preview_items)),
        hidden_items_note,
        "\n\nПозиций: ",
        f"{len(cart)} · Товаров: {total_quantity}",
        "\n",
        Bold(f"Итого: {format_money(total_sum)} ₽"),
        "\n\nПосле подтверждения данные сохранятся в PostgreSQL. ",
        "Оплата не потребуется, ресторан заказ не получит.",
    )


def get_order_confirm_message(order_id: int) -> Text:
    return Text(
        "✅ ",
        Bold(f"Демо-заказ №{order_id} оформлен"),
        "\n\nСценарий завершён: данные сохранены в PostgreSQL, а корзина очищена.\n\n",
        "Оплата не списывалась, заказ не передан ресторану.\n\n",
        Bold("Спасибо, что протестировали PizzaForge!"),
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
    Bold("Что закажем?"),
    "\n\n",
    "Выберите категорию. Внутри — состав, цена и добавление в корзину одним нажатием.",
)

owner_message = Text(
    "ℹ️ ",
    Bold("О проекте PizzaForge"),
    "\n\n",
    "Это работающий демо-бот, а не макет. Он показывает полный путь клиента: ",
    "меню, корзину, расчёт суммы и оформление заказа.\n\n",
    Bold("Что под капотом:"),
    "\n🐍 Python · aiogram · SQLAlchemy",
    "\n🐘 PostgreSQL · Alembic",
    "\n🐳 Docker Compose · тесты · CI/CD\n\n",
    "Проект развёрнут на удалённом сервере, а изменения проходят автоматические проверки.\n\n",
    Bold("Исходный код открыт на GitHub."),
)

contact_message = Text(
    "💬 ",
    Bold("Обсудим ваш Telegram-бот"),
    "\n\n",
    "Техническое задание не нужно. Достаточно описать идею своими словами.\n\n",
    "Я помогу продумать сценарий и оценить объём работы.\n\n",
    "Кнопка откроет чат и подставит готовое сообщение — ",
    Bold("оно не отправится автоматически."),
)
