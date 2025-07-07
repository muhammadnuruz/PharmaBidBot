from django.contrib import admin
from .models import Order


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'staff', 'price', 'status', 'created_at')
    list_display_links = ('id', 'user')
    list_filter = ('status', 'created_at')
    search_fields = ('user__full_name', 'staff__full_name', 'price', 'description')
    autocomplete_fields = ('user', 'staff')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)

    fieldsets = (
        ('📦 Buyurtma haqida', {
            'fields': ('user', 'staff', 'image', 'price', 'description')
        }),
        ('⚙️ Holati', {
            'fields': ('status',)
        }),
        ('🕒 Vaqtlar', {
            'fields': ('created_at', 'updated_at')
        }),
    )

    actions = ['mark_as_closed', 'mark_as_cancelled']

    @admin.action(description='✅ Tanlangan buyurtmalarni "Закрыто" qilish')
    def mark_as_closed(self, request, queryset):
        updated = queryset.update(status='closed')
        self.message_user(request, f"{updated} ta buyurtma закрыто qilindi.")

    @admin.action(description='❌ Tanlangan buyurtmalarni "Отменено" qilish')
    def mark_as_cancelled(self, request, queryset):
        updated = queryset.update(status='cancelled')
        self.message_user(request, f"{updated} ta buyurtma отменено qilindi.")
