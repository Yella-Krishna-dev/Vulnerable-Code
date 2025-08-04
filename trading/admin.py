from django.contrib import admin
from .models import UserProfile, Transaction


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'cash_balance', 'gold_balance')
    search_fields = ('user__username', 'user__email')
    list_filter = ('cash_balance', 'gold_balance')


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'type', 'amount', 'price', 'timestamp')
    list_filter = ('type', 'timestamp')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('timestamp',)
    date_hierarchy = 'timestamp' 