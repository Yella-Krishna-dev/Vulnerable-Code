from django.urls import path
from . import views

urlpatterns = [
    path('search/', views.search_products, name='search_products'),
    path('login/', views.login_user, name='login_user'),
    path('delete-order/', views.delete_order, name='delete_order'),
    path('user-orders/', views.get_user_orders, name='get_user_orders'),
    path('update-product/', views.update_product, name='update_product'),
    path('advanced-search/', views.advanced_search, name='advanced_search'),
    path('product-details/', views.get_product_details, name='get_product_details'),
    path('check-product/', views.check_product_exists, name='check_product_exists'),
] 