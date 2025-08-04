from django.contrib import admin
from .models import Product, Order


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'created_at')
    search_fields = ('name', 'description')
    list_filter = ('price', 'created_at')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'product', 'quantity', 'total_price', 'order_date')
    list_filter = ('order_date', 'product')
    search_fields = ('user__username', 'product__name')
    readonly_fields = ('order_date',)
    date_hierarchy = 'order_date' 