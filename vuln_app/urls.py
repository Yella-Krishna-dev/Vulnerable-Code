from django.urls import path
from . import views

urlpatterns = [
    path('api/sell-gold', views.sell_gold, name='sell_gold'),
    path('api/get-user', views.get_current_user, name='get_current_user'),
    path('api/update-gold', views.update_gold, name='update_gold'),
    path('api/validate-otp', views.validate_otp, name='validate_otp'),
] 