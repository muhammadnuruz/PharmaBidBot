import os
import django
from asgiref.sync import sync_to_async

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'PharmBidBot.settings')
django.setup()

from apps.telegram_users.models import TelegramUsers


@sync_to_async
def get_telegram_users():
    return list(TelegramUsers.objects.only('chat_id'))


@sync_to_async
def get_pharmacy_staffs():
    return list(TelegramUsers.objects.filter(is_staff=True))


@sync_to_async
def get_user_by_chat_id(chat_id: int):
    try:
        return TelegramUsers.objects.get(chat_id=chat_id)
    except TelegramUsers.DoesNotExist:
        return None


@sync_to_async
def get_user_by_id(_id: int):
    try:
        return TelegramUsers.objects.get(id=_id)
    except TelegramUsers.DoesNotExist:
        return None


@sync_to_async
def create_user_by_chat_id(chat_id: int,
                           full_name: str,
                           phone_number: str,
                           username: str,
                           location_lat: float,
                           location_lng: float) -> TelegramUsers:
    try:
        user, created = TelegramUsers.objects.get_or_create(
            chat_id=chat_id,
            defaults={
                "full_name": full_name,
                "phone_number": phone_number,
                "username": username,
                "location_lat": location_lat,
                "location_lng": location_lng
            }
        )
        return user
    except Exception as e:
        print(f"[create_user_by_chat_id ERROR]: {e}")
        return None


@sync_to_async
def update_user_by_chat_id(
        chat_id: int,
        full_name: str = None,
        username: str = None,
        phone_number: str = None,
        location_lat: float = None,
        location_lng: float = None) -> TelegramUsers | None:
    try:
        user = TelegramUsers.objects.get(chat_id=chat_id)
        if full_name is not None:
            user.full_name = full_name
        if username is not None:
            user.username = username
        if phone_number is not None:
            user.phone_number = phone_number
        if location_lat is not None:
            user.location_lat = location_lat
        if location_lng is not None:
            user.location_lng = location_lng
        user.save()
        return user
    except TelegramUsers.DoesNotExist:
        return None
