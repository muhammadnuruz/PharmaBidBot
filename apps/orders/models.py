from django.db import models

from apps.telegram_users.models import TelegramUsers


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'В ожидании'),
        ('closed', 'Закрыто'),
        ('cancelled', 'Отменено'),
    ]
    user = models.ForeignKey(TelegramUsers, verbose_name="Пользователь", on_delete=models.CASCADE,
                             related_name='orders')
    staff = models.ForeignKey(
        TelegramUsers,
        verbose_name="Сотрудник",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='deliveries'
    )
    image = models.CharField("Изображение")
    price = models.CharField("Цена", max_length=100, null=True)
    description = models.TextField("Описание", null=True)
    status = models.CharField("Статус", max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order #{self.id} - {self.user.full_name} ({self.get_status_display()})"

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Order"
        verbose_name_plural = "Orders"
