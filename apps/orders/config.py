import os
import django
from asgiref.sync import sync_to_async

from apps.telegram_users.config import get_user_by_chat_id

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'PharmBidBot.settings')
django.setup()

from apps.orders.models import Order
from apps.telegram_users.models import TelegramUsers


@sync_to_async
def get_order_by_id(_id: int):
    try:
        return Order.objects.get(id=_id)
    except Order.DoesNotExist:
        return None


@sync_to_async
def get_orders_queryset_for_user(user):
    if user.is_staff:
        return list(Order.objects.select_related("user").filter(staff=user).order_by("-created_at"))
    else:
        return list(Order.objects.select_related("staff").filter(user=user).order_by("-created_at"))


async def get_my_orders(chat_id: int):
    user = await get_user_by_chat_id(chat_id)
    if user is None:
        return []
    return await get_orders_queryset_for_user(user)


@sync_to_async
def create_order(
        user: TelegramUsers,
        image: str,
) -> Order:
    return Order.objects.create(
        user=user,
        image=image,
    )


@sync_to_async
def update_order(order_id: int, staff_id: int, price: str, description: str):
    try:
        order = Order.objects.get(id=order_id)
        staff = TelegramUsers.objects.get(chat_id=staff_id)
        order.staff = staff
        order.price = price
        order.description = description
        order.status = "closed"
        order.save()
        return True
    except Exception:
        return False


@sync_to_async
def get_order_with_user(order_id: int):
    return Order.objects.select_related("user").get(id=order_id)


@sync_to_async
def get_pending_orders():
    return list(
        Order.objects.filter(status="pending").order_by("-created_at")
    )
