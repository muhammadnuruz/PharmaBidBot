from django.contrib import admin
from .models import TelegramUsers


@admin.register(TelegramUsers)
class TelegramUsersAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'full_name', 'chat_id', 'username', 'phone_number',
        'is_staff', 'location_lat', 'location_lng', 'created_at', 'updated_at'
    )
    list_display_links = ('id', 'full_name')
    list_filter = ('is_staff', 'created_at', 'updated_at')
    search_fields = ('full_name', 'username', 'phone_number', 'chat_id')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)

    fieldsets = (
        (None, {
            'fields': ('chat_id', 'full_name', 'username', 'phone_number', 'is_staff')
        }),
        ('📍 Локация', {
            'fields': ('location_lat', 'location_lng')
        }),
        ('🕒 Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser
