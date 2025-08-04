from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('reset-password/', views.reset_password, name='reset_password'),
    path('change-password/', views.change_password, name='change_password'),
    path('price/', views.price, name='gold_price'),
    path('buy/', views.buy_gold, name='buy_gold'),
    path('sell/', views.sell_gold, name='sell_gold'),
    path('balance/', views.balance, name='balance'),
    path('transactions/', views.get_transactions, name='transactions'),
] 