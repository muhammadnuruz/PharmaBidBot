from django.db import models


class TelegramUsers(models.Model):
    chat_id = models.CharField("ИДЕНТИФИКАТОР", max_length=250, unique=True)
    username = models.CharField("Username", max_length=100, null=True)
    full_name = models.CharField("Полное имя", max_length=100)
    phone_number = models.CharField("Номер телефона", max_length=15, null=True)
    is_staff = models.BooleanField("Это рабочий?", default=False)
    location_lat = models.FloatField("Широта", blank=True, null=True)
    location_lng = models.FloatField("Долгота", blank=True, null=True)
    created_at = models.DateTimeField("Создано в", auto_now_add=True)
    updated_at = models.DateTimeField("Обновлено в", auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Telegram User"
        verbose_name_plural = "Telegram Users"

    def __str__(self):
        return f"{self.full_name} ({'Staff' if self.is_staff else 'User'})"
